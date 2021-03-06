import os, tempfile, logging

from dcplib.etl import DSSExtractor

from dcpquery.db.materialized_views import create_materialized_view_tables
from dcpquery.etl.load import BundleLoader
from dcpquery.etl.transform import transform_bundle

from .. import config

logger = logging.getLogger(__name__)


def update_process_join_table():
    config.db_session.execute(
        """
        Insert INTO process_join_table (child_process_uuid, parent_process_uuid)
          SELECT * FROM (
              WITH
                  input_files_table AS (
                                        SELECT
                                               process_uuid AS child_process,
                                               file_uuid    AS input_file_uuid
                                        FROM process_file_join_table
                                        WHERE process_file_connection_type = 'INPUT_ENTITY'
                                      ),

                  output_files_table AS (
                                          SELECT
                                                 process_uuid AS parent_process,
                                                 file_uuid AS output_file_uuid
                                        FROM process_file_join_table
                                        WHERE process_file_connection_type = 'OUTPUT_ENTITY'
                                      )
                  SELECT
                         input_files_table.child_process,
                         output_files_table.parent_process
                  FROM input_files_table, output_files_table
       WHERE input_files_table.input_file_uuid = output_files_table.output_file_uuid) AS temp_tables
       ON CONFLICT DO NOTHING;
        """
    )
    config.db_session.commit()


def dcpquery_etl_finalizer(extractor):
    create_materialized_view_tables()
    update_process_join_table()


def etl_one_bundle(bundle_uuid, bundle_version):
    extractor = DSSExtractor(staging_directory=tempfile.gettempdir(), dss_client=config.dss_client)
    os.makedirs(f"{extractor.sd}/files", exist_ok=True)
    os.makedirs(f"{extractor.sd}/bundles", exist_ok=True)
    _, _, files_to_fetch = extractor.get_files_to_fetch_for_bundle(bundle_uuid, bundle_version)
    for f in files_to_fetch:
        extractor.get_file(f, bundle_uuid, bundle_version)

    bundle_path = f"{extractor.sd}/bundles/{bundle_uuid}.{bundle_version}"
    bundle_manifest_path = f"{extractor.sd}/bundle_manifests/{bundle_uuid}.{bundle_version}.json"
    tb = transform_bundle(bundle_uuid=bundle_uuid, bundle_version=bundle_version, bundle_path=bundle_path,
                          bundle_manifest_path=bundle_manifest_path, extractor=extractor)
    BundleLoader().load_bundle(extractor=extractor, transformer=transform_bundle, bundle=tb)
    config.db_session.commit()

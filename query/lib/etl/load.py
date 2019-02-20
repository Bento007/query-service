import pylru
from psycopg2 import IntegrityError

from query.lib.etl.links_file_transform import LinksFileTransform
from query.lib.logger import logger
from query.lib.model import Bundle
from query.lib.db.database import PostgresDatabase, Tables


class Loader:

    def load(self, bundle: Bundle, transformed_bundle: dict):
        raise NotImplementedError()


class PostgresLoader(Loader):

    def __init__(self, db: PostgresDatabase):
        self._db = db
        self._existing_view_names = set([])
        self._inserted_files = pylru.lrucache(1000)

    def load(self, bundle: Bundle, transformed_bundle: dict):
        with self._db.transaction() as (_, tables):
            self._prepare_database(tables, bundle)
        with self._db.transaction() as (_, tables):
            self._insert_into_database(tables, bundle, transformed_bundle)

    def _prepare_database(self, tables: Tables, bundle: Bundle):
        # get table names for tables implied by the bundle manifest
        view_names_to_type_mapping = dict([(f.schema_type_plural, f.schema_type) for f in bundle.files])
        implied_view_names = set(f.schema_type_plural for f in bundle.files if f.normalizable)

        # if there are views implied in the manifest not recorded in PostgresLoader, refresh
        if len(implied_view_names - self._existing_view_names) > 0:
            self._existing_view_names = set(tables.files.select_views())

        # create view tables still outstanding
        for view_name in implied_view_names - self._existing_view_names:
            logger.info(f"Creating view: {view_name}")
            try:
                tables.files.create_view(view_name, view_names_to_type_mapping[view_name])
            except IntegrityError:
                logger.info(f"View already exists: {view_name}")

    def _insert_into_database(self, tables: Tables, bundle: Bundle, transformed_bundle: dict):
        # insert the bundle
        tables.bundles.insert(bundle, transformed_bundle)

        # insert files, and join table entry
        for file in bundle.files:
            if file.fqid not in self._inserted_files:
                tables.files.insert(file)
                if file.metadata.name == "links.json":
                    LinksFileTransform().links_file_transformer(tables, file['links'])
            self._inserted_files[file.fqid] = True
            tables.bundles_files.insert(
                bundle_uuid=bundle.uuid,
                bundle_version=bundle.version,
                file_uuid=file.uuid,
                file_version=file.metadata.version
            )

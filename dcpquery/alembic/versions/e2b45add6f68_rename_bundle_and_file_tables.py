"""rename_bundle_and_file_tables

Revision ID: e2b45add6f68
Revises: 7597ca0971e5
Create Date: 2019-07-03 14:30:49.987853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2b45add6f68'
down_revision = '9fa7918d332b'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('bundles', 'bundles_all_versions')
    op.rename_table('files', 'files_all_versions')
    op.execute(
        """
        CREATE OR REPLACE RULE bundle_table_ignore_duplicate_inserts AS
            ON INSERT TO bundles_all_versions
                WHERE EXISTS (
                  SELECT 1
                FROM bundles_all_versions
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE RULE file_table_ignore_duplicate_inserts AS
            ON INSERT TO files_all_versions
                WHERE EXISTS (
                  SELECT 1
                FROM files_all_versions
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
        """
    )
    op.execute(
        """
          CREATE OR REPLACE VIEW files AS
          SELECT * FROM files_all_versions
          WHERE (uuid, version) IN (SELECT uuid, max(version) FROM files_all_versions GROUP BY uuid)
        """
    )
    op.execute(
        """
          CREATE OR REPLACE VIEW bundles AS
          SELECT * FROM bundles_all_versions
          WHERE (uuid, version) IN (SELECT uuid, max(version) FROM bundles_all_versions GROUP BY uuid)
        """
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS files CASCADE;")
    op.execute("DROP VIEW IF EXISTS bundles CASCADE ;")
    op.rename_table('bundles_all_versions', 'bundles')
    op.rename_table('files_all_versions', 'files')
    op.execute("DROP RULE IF EXISTS file_table_ignore_duplicate_inserts ON files_all_versions;")
    op.execute("DROP RULE IF EXISTS bundle_table_ignore_duplicate_inserts ON bundles_all_versions;")

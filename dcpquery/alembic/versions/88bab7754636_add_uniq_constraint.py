"""add unique req to process_process combo

Revision ID: 88bab7754636
Revises: e2b45add6f68
Create Date: 2019-07-26 11:28:06.281752

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '88bab7754636'
down_revision = 'b56789b3d784'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unq_process_combo', 'process_join_table',
                                ['child_process_uuid', 'parent_process_uuid'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unq_process_combo', 'process_join_table', type_='unique')
    # ### end Alembic commands ###
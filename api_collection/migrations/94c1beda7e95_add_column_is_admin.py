"""Add column is_admin

Revision ID: 94c1beda7e95
Revises: 77927bff78c1
Create Date: 2019-08-10 11:04:03.190940

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '94c1beda7e95'
down_revision = '77927bff78c1'
branch_labels = ()
depends_on = None


def upgrade():
    op.add_column(
        'tbl_users',
        sa.Column('is_admin', sa.Boolean(),
                  server_default=sa.false(), nullable=False))
    op.alter_column(
        'tbl_users',
        column_name='is_admin',
        server_default=sa.null())


def downgrade():
    op.drop_column('tbl_users', 'is_admin')

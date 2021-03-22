"""Create usage_logs table

Revision ID: 77927bff78c1
Revises:
Create Date: 2019-06-13 21:52:23.960250

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils as su

# revision identifiers, used by Alembic.
revision = '77927bff78c1'
down_revision = '76f8b247fb87'
branch_labels = ('default',)
depends_on = None


def upgrade():
    op.create_table(
        'tbl_usage_logs',
        sa.Column('id', su.UUIDType(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('instance_name', sa.Unicode(length=255), nullable=False),
        sa.Column('instance_quantity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['tbl_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tbl_usage_logs_created_at'),
                    'tbl_usage_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_tbl_usage_logs_instance_name'),
                    'tbl_usage_logs', ['instance_name'], unique=False)
    op.create_index(op.f('ix_tbl_usage_logs_instance_quantity'),
                    'tbl_usage_logs', ['instance_quantity'], unique=False)
    op.create_index(op.f('ix_tbl_usage_logs_user_id'),
                    'tbl_usage_logs', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_tbl_usage_logs_user_id'),
                  table_name='tbl_usage_logs')
    op.drop_index(op.f('ix_tbl_usage_logs_instance_quantity'),
                  table_name='tbl_usage_logs')
    op.drop_index(op.f('ix_tbl_usage_logs_instance_name'),
                  table_name='tbl_usage_logs')
    op.drop_index(op.f('ix_tbl_usage_logs_created_at'),
                  table_name='tbl_usage_logs')
    op.drop_table('tbl_usage_logs')

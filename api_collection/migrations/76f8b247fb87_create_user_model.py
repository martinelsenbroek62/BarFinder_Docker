"""create user model

Revision ID: 76f8b247fb87
Revises:
Create Date: 2019-06-05 23:05:20.124616

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import EmailType, PasswordType

# revision identifiers, used by Alembic.
revision = '76f8b247fb87'
down_revision = None
branch_labels = ('users',)
depends_on = None


def upgrade():
    op.create_table(
        'tbl_users',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('email', EmailType, nullable=False),
        sa.Column('password',
                  PasswordType(schemes=['pbkdf2_sha512']),
                  nullable=False),
        sa.Column('created_at',
                  sa.DateTime(timezone=True),
                  nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    op.create_index(op.f('ix_tbl_users_created_at'),
                    'tbl_users', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_tbl_users_created_at'), table_name='tbl_users')
    op.drop_table('tbl_users')

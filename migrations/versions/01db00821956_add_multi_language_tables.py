"""add multi language tables

Revision ID: 01db00821956
Revises: 29b91fdfb6c1
Create Date: 2025-01-28 20:54:42.432525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01db00821956'
down_revision = '29b91fdfb6c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('languages',
    sa.Column('id', sa.BINARY(length=16), nullable=False),
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.BINARY(length=16), nullable=True),
    sa.Column('updated_by', sa.BINARY(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_general_ci'
    )
    op.create_table('translations',
    sa.Column('id', sa.BINARY(length=16), nullable=False),
    sa.Column('key', sa.String(length=255), nullable=False),
    sa.Column('context', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.BINARY(length=16), nullable=True),
    sa.Column('updated_by', sa.BINARY(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_general_ci'
    )
    op.create_table('translation_values',
    sa.Column('id', sa.BINARY(length=16), nullable=False),
    sa.Column('translation_id', sa.BINARY(length=16), nullable=False),
    sa.Column('language_id', sa.BINARY(length=16), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.BINARY(length=16), nullable=True),
    sa.Column('updated_by', sa.BINARY(length=16), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], ),
    sa.ForeignKeyConstraint(['translation_id'], ['translations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_general_ci'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('translation_values')
    op.drop_table('translations')
    op.drop_table('languages')
    # ### end Alembic commands ###

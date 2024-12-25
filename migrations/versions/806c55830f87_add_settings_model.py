"""Add settings model

Revision ID: 806c55830f87
Revises: 2df724ea1027
Create Date: 2024-12-21 21:25:17.226672

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '806c55830f87'
down_revision = '2df724ea1027'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('setting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=200),
               type_=sa.String(length=150),
               nullable=False)
        batch_op.alter_column('auth_provider',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('auth_provider',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.String(length=150),
               type_=mysql.VARCHAR(length=200),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=150),
               nullable=False)

    op.drop_table('setting')
    # ### end Alembic commands ###
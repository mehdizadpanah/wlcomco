"""Rename Notification Table

Revision ID: f6c4fa27dbb0
Revises: 0c7f05f55a7c
Create Date: 2025-01-09 20:15:53.533801

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f6c4fa27dbb0'
down_revision = '0c7f05f55a7c'
branch_labels = None
depends_on = None


def upgrade():
    # Get the current database connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check if 'notification' table already exists
    if 'notification' not in inspector.get_table_names():
        op.create_table(
            'notification',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('send_via', sa.Enum('email', 'sms'), nullable=False),
            sa.Column('content_type', sa.Enum('text', 'html'), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('subject', sa.String(length=255), nullable=True),
            sa.Column('body', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('updated_by', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    # Rename table only if it exists
    if 'notification_template' in inspector.get_table_names():
        with op.batch_alter_table('notification_template', schema=None) as batch_op:
            batch_op.drop_index('name')

        op.drop_table('notification_template')

    # Alter columns in the 'user' table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'password',
            existing_type=mysql.VARCHAR(length=200),
            type_=sa.String(length=150),
            nullable=False
        )
        batch_op.alter_column(
            'auth_provider',
            existing_type=mysql.VARCHAR(length=50),
            nullable=True
        )


def downgrade():
    # Downgrade: Revert changes
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Alter columns in the 'user' table
    with op.batch_alter_table('user', schema=None) as batch_op:
        # اطمینان از نوع و nullable بودن ستون password
        batch_op.alter_column(
            'password',
            existing_type=sa.String(length=150),  # تغییر داده شده از 150 به 200
            type_=sa.String(length=200),
            nullable=True
        )

        # اطمینان از نوع و nullable بودن ستون auth_provider
        batch_op.alter_column(
            'auth_provider',
            existing_type=sa.String(length=50),
            nullable=False,
            server_default="local"
        )

    # Check if 'notification_template' does not exist before creating
    if 'notification_template' not in inspector.get_table_names():
        op.create_table(
            'notification_template',
            sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
            sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
            sa.Column('send_via', mysql.ENUM('email', 'sms'), nullable=False),
            sa.Column('content_type', mysql.ENUM('text', 'html'), nullable=False),
            sa.Column('description', mysql.TEXT(), nullable=True),
            sa.Column('subject', mysql.VARCHAR(length=255), nullable=True),
            sa.Column('body', mysql.TEXT(), nullable=False),
            sa.Column('created_at', mysql.DATETIME(), nullable=True),
            sa.Column('updated_at', mysql.DATETIME(), nullable=True),
            sa.Column('created_by', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
            sa.Column('updated_by', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
            sa.PrimaryKeyConstraint('id'),
            mysql_collate='latin1_swedish_ci',
            mysql_default_charset='latin1',
            mysql_engine='InnoDB'
        )

    if 'notification_template' in inspector.get_table_names():
        with op.batch_alter_table('notification_template', schema=None) as batch_op:
            batch_op.create_index('name', ['name'], unique=True)

    op.drop_table('notification')

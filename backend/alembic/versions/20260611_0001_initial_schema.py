"""initial schema

Revision ID: 20260611_0001
Revises:
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260611_0001"
down_revision = None
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    return sa.inspect(bind).has_table(table_name)


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    if not sa.inspect(bind).has_table(table_name):
        return False
    return any(column["name"] == column_name for column in sa.inspect(bind).get_columns(table_name))


def upgrade() -> None:
    if not table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    elif not column_exists("users", "is_admin"):
        op.add_column("users", sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False))

    if not table_exists("server_settings"):
        op.create_table(
            "server_settings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("app_name", sa.String(length=80), nullable=False),
            sa.Column("external_url", sa.String(length=255), nullable=False),
            sa.Column("allow_registration", sa.Boolean(), nullable=False),
            sa.Column("setup_completed", sa.Boolean(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("shopping_lists"):
        op.create_table(
            "shopping_lists",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("list_members"):
        op.create_table(
            "list_members",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("list_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["list_id"], ["shopping_lists.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("list_id", "user_id", name="uq_list_member"),
        )

    if not table_exists("shopping_items"):
        op.create_table(
            "shopping_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("list_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("quantity", sa.String(length=80), nullable=False),
            sa.Column("is_checked", sa.Boolean(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["list_id"], ["shopping_lists.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("list_invites"):
        op.create_table(
            "list_invites",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("token", sa.String(length=80), nullable=False),
            sa.Column("list_id", sa.Integer(), nullable=False),
            sa.Column("created_by_id", sa.Integer(), nullable=False),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["list_id"], ["shopping_lists.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_list_invites_token"), "list_invites", ["token"], unique=True)
    else:
        if not column_exists("list_invites", "used_at"):
            op.add_column("list_invites", sa.Column("used_at", sa.DateTime(), nullable=True))
        if not column_exists("list_invites", "expires_at"):
            op.add_column("list_invites", sa.Column("expires_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    for table_name in ("list_invites", "shopping_items", "list_members", "shopping_lists", "server_settings", "users"):
        if table_exists(table_name):
            op.drop_table(table_name)

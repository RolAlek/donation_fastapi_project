"""Create Users table

Revision ID: ca37abb8923f
Revises: 4a75ea3edc6d
Create Date: 2024-07-09 17:18:59.974148

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ca37abb8923f"
down_revision: Union[str, None] = "4a75ea3edc6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("birthday", sa.DateTime(), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")

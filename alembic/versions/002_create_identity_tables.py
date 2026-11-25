"""create identity, session, checkout, and purchase history tables

Revision ID: 002_create_identity
Revises: 001_create_contacts
Create Date: 2026-11-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_create_identity"
down_revision: Union[str, Sequence[str], None] = "001_create_contacts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "registration_status",
            sa.String(length=16),
            server_default="guest",
            nullable=False,
        ),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone_e164", sa.String(length=16), nullable=True),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_identities_email_lower",
        "identities",
        [sa.text("lower(email)")],
        unique=True,
        postgresql_where=sa.text("email IS NOT NULL"),
    )
    op.create_index(
        "uq_identities_phone_e164",
        "identities",
        ["phone_e164"],
        unique=True,
        postgresql_where=sa.text("phone_e164 IS NOT NULL"),
    )
    op.create_table(
        "session_credentials",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("identity_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["identity_id"], ["identities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_session_credentials_token_hash"),
    )
    op.create_index(
        "ix_session_credentials_identity_id",
        "session_credentials",
        ["identity_id"],
    )
    op.create_table(
        "identity_checkout_states",
        sa.Column("identity_id", sa.Uuid(), nullable=False),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["identity_id"], ["identities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("identity_id"),
    )
    op.create_table(
        "identity_purchase_history_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("identity_id", sa.Uuid(), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["identity_id"], ["identities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_identity_purchase_history_identity_id",
        "identity_purchase_history_entries",
        ["identity_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_identity_purchase_history_identity_id",
        table_name="identity_purchase_history_entries",
    )
    op.drop_table("identity_purchase_history_entries")
    op.drop_table("identity_checkout_states")
    op.drop_index("ix_session_credentials_identity_id", table_name="session_credentials")
    op.drop_table("session_credentials")
    op.drop_index("uq_identities_phone_e164", table_name="identities")
    op.drop_index("uq_identities_email_lower", table_name="identities")
    op.drop_table("identities")

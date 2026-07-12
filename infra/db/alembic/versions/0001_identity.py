"""0001 identity: tenants, users, memberships."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "tenants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("class", sa.Text(), nullable=False),
        sa.Column("motor_version", sa.Text(), nullable=False, server_default=sa.text("'0.1.0'")),
        sa.Column(
            "inference_policy", sa.Text(), nullable=False, server_default=sa.text("'local_only'")
        ),
        sa.Column("data_residency", sa.Text(), nullable=False, server_default=sa.text("'eu'")),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'active'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("class IN ('own', 'client')", name="ck_tenants_class"),
        sa.UniqueConstraint("name", name="uq_tenants_name"),
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'active'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "memberships",
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False
        ),
        sa.Column("role", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "tenant_id", name="pk_memberships"),
        sa.CheckConstraint(
            "role IN ('owner', 'operator', 'client_user')", name="ck_memberships_role"
        ),
    )

    op.execute("ALTER TABLE tenants OWNER TO devos_migrator")
    op.execute("ALTER TABLE users OWNER TO devos_migrator")
    op.execute("ALTER TABLE memberships OWNER TO devos_migrator")

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON tenants, users, memberships TO devos_api")
    op.execute("GRANT SELECT ON tenants, users, memberships TO devos_readonly")


def downgrade() -> None:
    op.drop_table("memberships")
    op.drop_table("users")
    op.drop_table("tenants")

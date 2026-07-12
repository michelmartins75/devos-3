"""0002 RLS: tenant_isolation on memberships and domain_probe."""

from alembic import op

revision = "0002_rls"
down_revision = "0001_identity"
branch_labels = None
depends_on = None

TENANT_ISOLATION_POLICY = """
CREATE POLICY tenant_isolation ON {table}
  AS PERMISSIVE FOR ALL
  TO devos_api, devos_readonly
  USING (
    current_setting('app.tenant_id', true) IS NOT NULL
    AND current_setting('app.tenant_id', true) <> ''
    AND tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  )
  WITH CHECK (
    current_setting('app.tenant_id', true) IS NOT NULL
    AND current_setting('app.tenant_id', true) <> ''
    AND tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  )
"""


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE domain_probe (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            label TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("ALTER TABLE domain_probe OWNER TO devos_migrator")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON domain_probe TO devos_api")
    op.execute("GRANT SELECT ON domain_probe TO devos_readonly")

    for table in ("memberships", "domain_probe"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(TENANT_ISOLATION_POLICY.format(table=table))

    op.execute(
        """
        CREATE VIEW domain_probe_view
        WITH (security_barrier = true, security_invoker = true) AS
        SELECT id, tenant_id, label, created_at
        FROM domain_probe
        """
    )
    op.execute("ALTER VIEW domain_probe_view OWNER TO devos_migrator")
    op.execute("GRANT SELECT ON domain_probe_view TO devos_api, devos_readonly")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS domain_probe_view")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON domain_probe")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON memberships")
    op.execute("DROP TABLE IF EXISTS domain_probe")

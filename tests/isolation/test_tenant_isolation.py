from uuid import UUID, uuid4

import psycopg
import pytest

pytestmark = pytest.mark.isolation


@pytest.fixture(autouse=True)
def _clean_isolation_tables(migrator_conn: psycopg.Connection) -> None:
    with migrator_conn.cursor() as cur:
        cur.execute("TRUNCATE domain_probe, memberships, tenants, users RESTART IDENTITY CASCADE")


def _set_tenant(cur: psycopg.Cursor, tenant_id: UUID | None) -> None:
    if tenant_id is None:
        cur.execute("RESET app.tenant_id")
    else:
        cur.execute("SELECT set_config('app.tenant_id', %s, true)", (str(tenant_id),))


def _seed_tenants(migrator_conn: psycopg.Connection) -> tuple[UUID, UUID]:
    tenant_a = uuid4()
    tenant_b = uuid4()
    suffix = str(tenant_a)[:8]
    with migrator_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tenants (
                id, name, class, motor_version, inference_policy, data_residency, status
            )
            VALUES
              (%s, %s, 'own', '0.1.0', 'unrestricted', 'eu', 'active'),
              (%s, %s, 'client', '0.1.0', 'local_only', 'eu', 'active')
            """,
            (tenant_a, f"tenant-a-{suffix}", tenant_b, f"tenant-b-{suffix}"),
        )
        cur.execute(
            """
            INSERT INTO domain_probe (tenant_id, label)
            VALUES (%s, 'probe-a'), (%s, 'probe-b')
            """,
            (tenant_a, tenant_b),
        )
    return tenant_a, tenant_b


def test_tenant_reads_only_own_rows(
    api_conn: psycopg.Connection, migrator_conn: psycopg.Connection
) -> None:
    tenant_a, tenant_b = _seed_tenants(migrator_conn)

    with api_conn.cursor() as cur:
        _set_tenant(cur, tenant_a)
        cur.execute("SELECT tenant_id, label FROM domain_probe ORDER BY label")
        rows = cur.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == tenant_a
        assert rows[0][1] == "probe-a"

        _set_tenant(cur, tenant_b)
        cur.execute("SELECT tenant_id, label FROM domain_probe ORDER BY label")
        rows = cur.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == tenant_b
        assert rows[0][1] == "probe-b"


def test_with_check_blocks_cross_tenant_write(
    api_conn: psycopg.Connection, migrator_conn: psycopg.Connection
) -> None:
    tenant_a, tenant_b = _seed_tenants(migrator_conn)

    with api_conn.cursor() as cur:
        _set_tenant(cur, tenant_a)
        with pytest.raises(
            (psycopg.errors.InsufficientPrivilege, psycopg.errors.CheckViolation)
        ):
            cur.execute(
                "INSERT INTO domain_probe (tenant_id, label) VALUES (%s, 'illegal')",
                (tenant_b,),
            )
        api_conn.rollback()

        _set_tenant(cur, tenant_a)
        cur.execute("SELECT id FROM domain_probe WHERE label = 'probe-a'")
        row = cur.fetchone()
        assert row is not None
        with pytest.raises(
            (psycopg.errors.InsufficientPrivilege, psycopg.errors.CheckViolation)
        ):
            cur.execute(
                "UPDATE domain_probe SET tenant_id = %s WHERE id = %s",
                (tenant_b, row[0]),
            )
        api_conn.rollback()


def _count(cur: psycopg.Cursor, query: str) -> int:
    cur.execute(query)  # type: ignore[arg-type]
    row = cur.fetchone()
    assert row is not None
    return int(row[0])


def test_no_context_returns_zero_rows(
    api_conn: psycopg.Connection, migrator_conn: psycopg.Connection
) -> None:
    _seed_tenants(migrator_conn)

    with api_conn.cursor() as cur:
        _set_tenant(cur, None)
        assert _count(cur, "SELECT count(*) FROM domain_probe") == 0
        assert _count(cur, "SELECT count(*) FROM memberships") == 0


def test_invalid_tenant_context_denied(
    api_conn: psycopg.Connection, migrator_conn: psycopg.Connection
) -> None:
    _seed_tenants(migrator_conn)

    with api_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', 'not-a-uuid', true)")
        with pytest.raises(psycopg.errors.InvalidTextRepresentation):
            cur.execute("SELECT count(*) FROM domain_probe")
        api_conn.rollback()

        cur.execute("SELECT set_config('app.tenant_id', '', true)")
        assert _count(cur, "SELECT count(*) FROM domain_probe") == 0


def test_indirect_paths_do_not_leak(
    api_conn: psycopg.Connection, migrator_conn: psycopg.Connection
) -> None:
    tenant_a, tenant_b = _seed_tenants(migrator_conn)

    with api_conn.cursor() as cur:
        _set_tenant(cur, tenant_a)

        assert _count(
            cur,
            """
            SELECT count(*)
            FROM domain_probe dp
            JOIN tenants t ON t.id = dp.tenant_id
            """,
        ) == 1

        assert _count(
            cur,
            """
            SELECT count(*)
            FROM domain_probe
            WHERE tenant_id IN (SELECT id FROM tenants)
            """,
        ) == 1

        assert _count(cur, "SELECT count(*) FROM domain_probe_view") == 1

        cur.execute("SELECT tenant_id FROM domain_probe_view")
        rows = cur.fetchall()
        assert all(row[0] == tenant_a for row in rows)
        assert tenant_b not in {row[0] for row in rows}


def test_rls_posture_audit(migrator_conn: psycopg.Connection) -> None:
    """CI guard: domain tables must have FORCE RLS and tenant_isolation policy."""
    with migrator_conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.relname
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'r'
              AND c.relname IN ('memberships', 'domain_probe')
              AND c.relrowsecurity = true
              AND c.relforcerowsecurity = true
            ORDER BY c.relname
            """
        )
        tables = {row[0] for row in cur.fetchall()}
        assert tables == {"domain_probe", "memberships"}

        cur.execute(
            """
            SELECT tablename
            FROM pg_policies
            WHERE schemaname = 'public'
              AND policyname = 'tenant_isolation'
              AND tablename IN ('memberships', 'domain_probe')
            """
        )
        policies = {row[0] for row in cur.fetchall()}
        assert policies == {"domain_probe", "memberships"}

        cur.execute(
            """
            SELECT c.relname, pg_get_userbyid(c.relowner) AS owner
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'r'
              AND c.relname IN ('memberships', 'domain_probe', 'tenants', 'users')
            """
        )
        owners = {row[0]: row[1] for row in cur.fetchall()}
        for table in ("memberships", "domain_probe", "tenants", "users"):
            assert owners[table] == "devos_migrator"

        cur.execute(
            """
            SELECT rolname, rolbypassrls
            FROM pg_roles
            WHERE rolname = 'devos_api'
            """
        )
        role = cur.fetchone()
        assert role is not None
        assert role[1] is False

        cur.execute(
            """
            SELECT rolname, rolbypassrls
            FROM pg_roles
            WHERE rolname = 'devos_migrator'
            """
        )
        migrator_role = cur.fetchone()
        assert migrator_role is not None
        assert migrator_role[1] is True

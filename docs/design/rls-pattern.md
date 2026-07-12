# Row-Level Security Pattern — DevOS 3.0

Every domain table in `devos_app` must follow this checklist from its first migration.
Isolation is enforced in PostgreSQL, not in application code.

## Roles

| Role | Purpose |
|------|---------|
- `devos_migrator` | Owns tables, runs Alembic DDL, has `BYPASSRLS` for migrations and seeds |
| `devos_api` | Application role, subject to RLS (`NOBYPASSRLS`) |
| `devos_readonly` | Reporting / distributed team read access, also subject to RLS |

Never grant `devos_api` ownership of domain tables.

## New domain table checklist

1. Add `tenant_id UUID NOT NULL REFERENCES tenants(id)` on every domain row.
2. Create the table in a migration executed as `devos_migrator`.
3. `ALTER TABLE ... OWNER TO devos_migrator`.
4. Grant DML to `devos_api`; grant `SELECT` to `devos_readonly` as needed.
5. `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.
6. `ALTER TABLE ... FORCE ROW LEVEL SECURITY`.
7. Create policy `tenant_isolation` for `devos_api` and `devos_readonly`:

```sql
CREATE POLICY tenant_isolation ON <table>
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
  );
```

8. Add or extend the sacred isolation suite in `tests/isolation/`.
9. Extend the RLS posture audit test when the table becomes part of the protected set.

## Tenant context

- Set context per transaction with `SELECT set_config('app.tenant_id', '<uuid>', true)` (`SET LOCAL` semantics).
- API middleware resolves tenant (provisional header today; ADR-003 will replace this) and binds context before any query.
- Workers must set context per job on a dedicated connection or reset between jobs.
- Missing or empty context must fail closed: zero visible rows, no writes.

## Views and functions

- Prefer `security_barrier = true` and `security_invoker = true` on views over domain data.
- Avoid `SECURITY DEFINER` functions that bypass RLS unless explicitly reviewed in an ADR.
- Do not expose cross-tenant joins outside RLS-protected base tables.

## CI guardrails

The `test_rls_posture_audit` test verifies:

- `FORCE ROW LEVEL SECURITY` on protected tables
- `tenant_isolation` policy present
- Table owner is `devos_migrator`, not `devos_api`
- `devos_api` does not have `BYPASSRLS`

## Reference implementation

See migration `infra/db/alembic/versions/0002_rls.py` and tests in `tests/isolation/`.

# DevOS 3.0

DevOS 3.0 is the ForgeWorks Digital multi-tenant consolidation platform. It is a greenfield foundation, not a rewrite: tenancy, isolation, auditability, and inference policy are native from day one, while proven DevOS v2 capabilities are transplanted deliberately.

The source of truth for scope and decisions starts in [`docs/charter/devos-3.0-carta-de-fundacao.md`](docs/charter/devos-3.0-carta-de-fundacao.md). Operational runbooks live in `docs/runbooks/`, architecture decisions in `docs/adr/`, execution orders in `docs/orders/`, model-routing references in `docs/model-routing/`, and design documents in `docs/design/`.

## Repository layout

```
devos-3/
├── apps/
│   ├── api/              FastAPI application (/health, tenant context middleware)
│   └── worker/           Agent runner placeholder (Leva 2)
├── packages/
│   ├── shared-types/     Shared constants and types
│   └── engines/          Engine packages (Leva 2)
├── infra/
│   ├── docker-compose.yml
│   ├── postgres/         Role bootstrap for local Postgres
│   └── db/               Alembic migrations
├── scripts/
│   └── seed_dev.py       Idempotent dev seed
├── tests/
│   ├── api/
│   └── isolation/        Sacred tenant isolation suite
└── docs/
```

## Quick start (local)

Requirements: Docker, Docker Compose, Python 3.12+.

```bash
# Start Postgres + API
docker compose -f infra/docker-compose.yml up --build -d

# Or run API against local Postgres after migrations:
pip install -e ".[dev]"
psql postgresql://postgres:postgres@localhost:5432/postgres -c "CREATE DATABASE devos_app;"
psql postgresql://postgres:postgres@localhost:5432/postgres -c "CREATE DATABASE devos_audit;"
psql postgresql://postgres:postgres@localhost:5432/devos_app -f infra/postgres/init-roles.sql
alembic -c infra/db/alembic.ini upgrade head
uvicorn devos_api.main:app --host 0.0.0.0 --port 8080
curl http://localhost:8080/health
```

Run migrations and the sacred isolation tests:

```bash
pytest -m isolation
pytest
```

Seed development tenants and users:

```bash
python scripts/seed_dev.py
```

Copy `.env.example` to `.env` to override connection strings.

## Documentation map

- [`docs/charter/devos-3.0-carta-de-fundacao.md`](docs/charter/devos-3.0-carta-de-fundacao.md) — foundation charter and execution plan
- [`docs/orders/leva-1/`](docs/orders/leva-1/) — Leva 1 dispatch index and OS-01 through OS-04
- [`docs/runbooks/ct130.md`](docs/runbooks/ct130.md) — CT130 / `devos3` infrastructure runbook
- [`docs/design/rls-pattern.md`](docs/design/rls-pattern.md) — RLS checklist for every domain table
- [`docs/model-routing/capabilities-matrix-template.md`](docs/model-routing/capabilities-matrix-template.md) — model capability matrix template

## OS-02 delivery (Cursor)

Leva 1 / Fase 1 foundation delivered in this branch:

- Monorepo skeleton (T1)
- FastAPI with structured JSON logging and provisional tenant header middleware (T2)
- CI: ruff, pyright, pytest, Postgres 16, migration smoke, Docker build (T3)
- Alembic migration `0001_identity`: `tenants`, `users`, `memberships` (T4)
- Alembic migration `0002_rls`: `domain_probe`, `tenant_isolation` policy, RLS pattern doc (T5)
- Sacred isolation suite in `tests/isolation/` (T6)
- Idempotent dev seed script (T7)

Target environment: CT130 (`192.168.179.130`) per [`docs/runbooks/ct130.md`](docs/runbooks/ct130.md).

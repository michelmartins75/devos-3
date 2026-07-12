# DevOS 3.0

> **Versão em português:** [README.md](README.md)

DevOS 3.0 is the ForgeWorks Digital multi-tenant consolidation platform. It is a greenfield foundation, not a rewrite: tenancy, isolation, auditability, and inference policy are native from day one, while proven DevOS v2 capabilities are transplanted deliberately.

The source of truth for scope and decisions starts in [`docs/charter/devos-3.0-carta-de-fundacao.md`](docs/charter/devos-3.0-carta-de-fundacao.md). Operational runbooks live in `docs/runbooks/`, architecture decisions in `docs/adr/`, execution orders in `docs/orders/`, model-routing references in `docs/model-routing/`, and design documents in `docs/design/`.

## Repository layout

```
devos-3/
├── apps/
│   ├── api/              FastAPI application
│   ├── web/              Operator console (React + Vite)
│   └── worker/           Agent runner placeholder (Leva 2)
├── packages/
│   ├── shared-types/
│   └── engines/
├── infra/
├── scripts/
├── tests/
└── docs/
```

## Quick start

```bash
docker compose -f infra/docker-compose.yml up --build -d
curl http://localhost:8080/health
# Console: http://localhost:3000
```

For local API development, migrations, tests, and seeding, see the full instructions in [README.md](README.md).

## Documentation map

- [`docs/charter/`](docs/charter/) — foundation charter
- [`docs/adr/`](docs/adr/) — architecture decision records
- [`docs/orders/leva-1/`](docs/orders/leva-1/) — Leva 1 execution orders
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution workflow
- [`GLOSSARIO.md`](GLOSSARIO.md) — glossary (Portuguese)

## Review ownership

| Area | Owner |
|------|-------|
| Infrastructure / CT130 | Codex |
| Code / CI / migrations | Cursor |
| ADRs / deep design | Claude Code |
| Support documentation | Gemini |

Target environment: CT130 (`192.168.179.130`).

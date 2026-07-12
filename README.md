# DevOS 3.0

> **English version:** [README.en.md](README.en.md)

O DevOS 3.0 é a plataforma multi-tenant de consolidação da ForgeWorks Digital. É uma fundação greenfield — não um rewrite: tenancy, isolamento, auditoria e política de inferência são nativos desde o dia um, enquanto as capacidades já provadas do DevOS v2 são transplantadas de forma deliberada.

A fonte da verdade de escopo e decisões está em [`docs/charter/devos-3.0-carta-de-fundacao.md`](docs/charter/devos-3.0-carta-de-fundacao.md). Runbooks operacionais em `docs/runbooks/`, decisões arquiteturais em `docs/adr/`, ordens de execução em `docs/orders/`, referências de roteamento de modelos em `docs/model-routing/` e documentos de design em `docs/design/`.

## Estrutura do repositório

```
devos-3/
├── apps/
│   ├── api/              API FastAPI (/health, /api/v1/status, tenant context)
│   ├── web/              Console operacional (React + Vite)
│   └── worker/           Agent runner placeholder (Leva 2)
├── packages/
│   ├── shared-types/     Constantes e tipos compartilhados
│   └── engines/          Pacotes de engines (Leva 2)
├── infra/
│   ├── docker-compose.yml
│   ├── postgres/         Bootstrap de roles Postgres
│   └── db/               Migrações Alembic
├── scripts/
│   └── seed_dev.py       Seed idempotente de dev
├── tests/
│   ├── api/
│   └── isolation/        Suíte sagrada de isolamento de tenant
└── docs/
```

## Quick start (local)

Requisitos: Docker, Docker Compose, Python 3.12+ (Node 22+ para desenvolvimento do web).

```bash
# Stack completa: Postgres + API + Web
docker compose -f infra/docker-compose.yml up --build -d
curl http://localhost:8080/health
# Console: http://localhost:3000

# Desenvolvimento API (Postgres local):
pip install -e ".[dev]"
psql postgresql://postgres:postgres@localhost:5432/postgres -c "CREATE DATABASE devos_app;"
psql postgresql://postgres:postgres@localhost:5432/postgres -c "CREATE DATABASE devos_audit;"
psql postgresql://postgres:postgres@localhost:5432/devos_app -f infra/postgres/init-roles.sql
alembic -c infra/db/alembic.ini upgrade head
uvicorn devos_api.main:app --host 0.0.0.0 --port 8080

# Desenvolvimento web:
cd apps/web && npm install && npm run dev
```

Testes e seed:

```bash
pytest -m isolation
pytest
python3 scripts/seed_dev.py
```

Copie `.env.example` para `.env` e `apps/web/.env.example` para `apps/web/.env` conforme necessário.

## Mapa da documentação

| Documento | Conteúdo |
|-----------|----------|
| [`docs/charter/`](docs/charter/) | Carta de fundação — fonte da verdade |
| [`docs/adr/`](docs/adr/) | Decisões arquiteturais (ADRs) |
| [`docs/orders/leva-1/`](docs/orders/leva-1/) | Ordens de serviço da Leva 1 |
| [`docs/runbooks/ct130.md`](docs/runbooks/ct130.md) | Runbook CT130 / `devos3` |
| [`docs/runbooks/onboarding-time.md`](docs/runbooks/onboarding-time.md) | Onboarding do time distribuído |
| [`docs/design/rls-pattern.md`](docs/design/rls-pattern.md) | Checklist RLS para tabelas de domínio |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Fluxo de contribuição |
| [`GLOSSARIO.md`](GLOSSARIO.md) | Glossário de termos |

## Quem revisa o quê

| Área | Dono | Agente default |
|------|------|----------------|
| Infra / CT130 | Codex | GPT via Codex |
| Código / CI / migrações | Cursor | Cursor |
| ADRs / design profundo | Claude Code | Claude |
| Documentação de apoio | Gemini | Gemini |
| Inferência local | Terra (Ollama) | qwen3 / qwen3-coder |

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para o fluxo completo de PR.

## Entregas Leva 1

- **OS-01** (Codex): infra CT130 — ver [`docs/runbooks/ct130.md`](docs/runbooks/ct130.md)
- **OS-02** (Cursor): monorepo + RLS + teste sagrado — ver [`docs/orders/leva-1/os-02-cursor-fundacao.md`](docs/orders/leva-1/os-02-cursor-fundacao.md)
- **OS-04** (Gemini/Cursor): documentação de nascença — este README, CONTRIBUTING, glossário, ADR stubs
- **Interface**: console operacional em `apps/web` (dashboard, health, contexto de tenant provisório)

Ambiente alvo: CT130 (`192.168.179.130`).

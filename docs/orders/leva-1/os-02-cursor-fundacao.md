# OS-02 · Cursor — Esqueleto do Monorepo + Fundação de Tenancy
**Ref.:** Carta de Fundação v1.2, Épicos F1 e F2.1–F2.2 · **Papel:** dono do desenvolvimento (D12) · **Fase:** 1

## Missão
Levantar o monorepo `devos-3` com CI desde o primeiro PR e entregar a fundação de tenancy: registro de tenants + Row-Level Security provado por teste automatizado. O produto desta OS é **o teste sagrado de isolamento verde no CI** — tudo o mais serve a ele.

## Contexto mínimo necessário
- O DevOS 3.0 é multi-tenant por fundação (Motor de base única, D1): **toda** tabela de domínio carrega `tenant_id` e RLS desde a primeira migração. Não existe "adicionar tenant depois".
- Isolamento é imposto **no banco** (D7), não na aplicação: a role `devos_api` está sujeita a RLS (`FORCE`), e o contexto de tenant entra por `SET app.tenant_id` por transação/conexão.
- Ambiente alvo: CT130 (OS-01, em paralelo). Desenvolvimento não espera o ambiente — use Postgres 16 local/CI idêntico.
- Engines e roteador de inferência são **leva 2**. Não antecipar.

## Tarefas (1 issue = 1 PR)

### T1 — Estrutura do monorepo
`apps/api`, `apps/worker` (placeholder), `packages/shared-types`, `packages/engines/` (vazio, leva 2), `infra/`, `docs/`, `.github/workflows/`.
*Aceite: árvore commitada; README raiz aponta pra carta em `docs/charter/`.*

### T2 — API base
FastAPI em `apps/api`: `/health` → 200, config por ambiente (pydantic-settings), estrutura de logging estruturado (JSON) com campo `tenant_id` desde já.
*Aceite: `docker compose up` local sobe API; `/health` = 200.*

### T3 — CI
GitHub Actions: lint (ruff) + typecheck (mypy ou pyright) + testes (pytest) + build da imagem em todo PR. Serviço Postgres 16 no workflow pra testes de integração.
*Aceite: branch protection na `main` — PR sem CI verde não mergeia.*

### T4 — Migração 0001: identidade
Alembic configurado. Migração 0001 cria:
- `tenants`: `id (uuid), name, class ('own'|'client'), motor_version, inference_policy (texto, preset — validação de valores fica pra F3), data_residency, status, created_at`
- `users`: `id, email (unique), display_name, status, created_at`
- `memberships`: `user_id, tenant_id, role ('owner'|'operator'|'client_user')`, PK composta
*Aceite: upgrade E downgrade rodam limpos no CI.*

### T5 — Migração 0002: RLS (⚠ gate: só mergeia após veredito do ADR-001 / OS-03)
- Função/convenção de contexto: `app.tenant_id` setado por request na API (middleware) e por job no worker.
- Política `tenant_isolation` (USING + WITH CHECK sobre `tenant_id = current_setting('app.tenant_id')::uuid`) aplicada a `memberships` e a uma tabela-cobaia `domain_probe` criada só pra prova.
- `ENABLE` + `FORCE ROW LEVEL SECURITY`; owner das tabelas ≠ `devos_api`.
- Template documentado em `docs/design/rls-pattern.md`: como TODA tabela de domínio futura nasce (checklist de migração).

### T6 — O TESTE SAGRADO
Suíte `tests/isolation/` que roda em todo CI, conectando como `devos_api`:
1. Cria tenant A e tenant B com dados em `domain_probe`.
2. Com contexto A: lê só A; **INSERT/UPDATE com `tenant_id` de B falha** (WITH CHECK).
3. Sem contexto setado: **zero linhas** em qualquer SELECT.
4. Tentativa de `SET app.tenant_id` inválido/vazio → acesso negado, não fallback.
5. Caminhos indiretos: JOIN, subquery, view sobre a cobaia — nada vaza.
*Aceite: suíte no CI, obrigatória, nomeada `isolation` — falhou, nada mergeia. Este teste é o produto (carta, §11: vazamento entre tenants = risco existencial).*

### T7 — Seed de desenvolvimento
Script idempotente: cria tenants `portalliz`, `zev-lur`, `nau` (classe `own`) + usuários Michel/Daniel/André com memberships.
*Aceite: rodável em dev e no CT130 sem efeito colateral em re-execução.*

## Definição de pronto da OS
- [ ] T1–T4 mergeados com CI verde
- [ ] ADR-001 emitido → T5 mergeado incorporando o veredito
- [ ] Teste sagrado (T6) verde e obrigatório no CI
- [ ] Seed (T7) validado no CT130 assim que OS-01 entregar

## Fora de escopo (não fazer)
- Tabelas de domínio do SSOT (`work_items`, `specs`, etc.) — leva 2 (F2.3), após o padrão RLS provado.
- Auth/JWT/OIDC — aguarda ADR-003 (OS-03). O middleware de contexto de tenant desta OS pode usar header interno provisório, marcado `# TODO(ADR-003)`.
- Roteador de inferência, registro de modelos, engines, worker real — leva 2.
- Qualquer chamada a modelo de IA — esta OS é fundação pura.

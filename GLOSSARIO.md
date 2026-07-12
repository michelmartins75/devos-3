# Glossário — DevOS 3.0

Termos do projeto, extraídos da carta de fundação v1.2. Em dúvida, consulte a carta — não invente definição.

| Termo | Definição |
|-------|-----------|
| **Tenant** | Unidade de isolamento lógico; todo dado de domínio carrega `tenant_id`. Clientes e projetos ForgeWorks coexistem como tenants distintos no mesmo Motor. |
| **Classe de tenant (`own` / `client`)** | `own` = projeto interno ForgeWorks (inferência nuvem permitida por default). `client` = cliente externo (default `local_only`, DSGVO-by-design). |
| **Motor** | Motor de base única compartilhado por todos os tenants — pipeline, engines e orchestrator versionados, não fork por tenant. |
| **Pinning** | Versão de Motor fixada por tenant (`tenants.motor_version`); promoção controlada por release gate. |
| **SSOT** | Single Source of Truth — PostgreSQL 16 no CT130 com RLS; dado + inferência de tenant `client` no mesmo perímetro local. |
| **RLS** | Row-Level Security — isolamento imposto no banco via política `tenant_isolation` e contexto `app.tenant_id`. |
| **Teste sagrado** | Suíte `tests/isolation/` que prova isolamento entre tenants; obrigatória no CI, falhou = nada mergeia. |
| **Loop interno** | Loop de validação executável (CT172) — fecha sozinho, rejeição alimenta DevOS. |
| **Loop externo** | Loop de release do cliente — fecha com humano, rejeição alimenta KnowledgeOS. |
| **Preset de inferência** | Política nomeada por tenant: `local_only` (default `client`), `eu_cloud`, `unrestricted` (default `own`). |
| **Capacidade** | O que um engine pede ao roteador: `reasoning`, `code_gen`, `embedding`, `triage` — nunca um modelo nomeado (D13). |
| **Registro de modelos** | Tabela de modelos/providers elegíveis; mapeamento capacidade→modelo é dado configurável por tenant, não código hardcoded. |
| **Leva** | Pacote de ordens de serviço despachadas em paralelo com gates de sincronização explícitos (ex.: Leva 1 = fundação). |
| **Ordem de serviço (OS)** | Dispatch documentado para um agente/dono com missão, tarefas, aceite e fora de escopo. |
| **ADR** | Architecture Decision Record — decisão cravada em `docs/adr/` (contexto → opções → decisão → consequências). |
| **Transplante** | Portar capacidade provada do v2 (engines, loop, GitHub) para a fundação 3.0 sem reescrever o que toca tenancy. |

Fonte: [`docs/charter/devos-3.0-carta-de-fundacao.md`](docs/charter/devos-3.0-carta-de-fundacao.md)

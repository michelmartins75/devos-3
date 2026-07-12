# ADR-001: Isolamento multi-tenant via RLS

- **Status:** proposto
- **Dono:** Claude Code (OS-03)
- **Gateia:** migração RLS (OS-02/T5), testes de isolamento

## Contexto

O DevOS 3.0 impõe isolamento de tenant no PostgreSQL via Row-Level Security, contexto `app.tenant_id` e política `tenant_isolation`. Este ADR documenta a revisão adversarial do desenho.

## Decisão

_Pendente — conteúdo técnico vem do Claude Code (OS-03)._

## Consequências

_Pendente._

Ver também: [`docs/design/rls-pattern.md`](../design/rls-pattern.md), [`tests/isolation/`](/tests/isolation/).

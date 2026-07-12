# Contribuindo com o DevOS 3.0

Obrigado por contribuir. Este repositório segue a carta de fundação v1.2 como fonte da verdade.

## Fluxo de trabalho

1. **1 issue = 1 PR** — escopo focado, critérios de aceite claros na issue.
2. **Branch** — use o prefixo `cursor/` para branches de agente cloud: `cursor/<descricao>-c7eb`.
3. **CI obrigatório** — ruff, pyright, pytest (incl. marker `isolation`) e smoke Alembic devem passar.
4. **Branch protection** — PR sem CI verde não mergeia na `main`.
5. **Revisor** — o dono da área revisa (tabela abaixo). Agentes podem tocar outras áreas (D12), mas o dono aprova.

## Donos por área

| Área | Dono primário | Revisor humano |
|------|---------------|----------------|
| Infra / CT130 / Postgres / Tailscale | Codex | Michel / Daniel |
| Código / testes / CI / migrações | Cursor | Michel / Daniel |
| ADRs / design adversarial | Claude Code | Michel / Daniel |
| Documentação de apoio | Gemini | Michel |
| Roteamento de inferência / engines | Cursor (Leva 2+) | Michel / Daniel |

## Commits

- Mensagens em inglês ou português, no imperativo: `feat(api): add status endpoint`.
- Prefixos comuns: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`.
- Referencie a OS ou issue quando aplicável: `feat(os-02): ...`.

## Migrações e RLS

**Regra:** nenhum merge que crie ou altere tabela de domínio sem seguir o checklist em [`docs/design/rls-pattern.md`](docs/design/rls-pattern.md).

Checklist mínimo:

- [ ] `tenant_id NOT NULL` em toda tabela de domínio
- [ ] Owner = `devos_migrator`, não `devos_api`
- [ ] `ENABLE` + `FORCE ROW LEVEL SECURITY`
- [ ] Política `tenant_isolation` aplicada
- [ ] Testes em `tests/isolation/` atualizados ou estendidos

## Teste sagrado

O marker `isolation` é **obrigatório** no CI. Falhou, nada mergeia. Não desabilite, não skippe, não enfraqueça.

```bash
pytest -m isolation
```

## Desenvolvimento local

Ver [`README.md`](README.md) para stack Docker, migrações Alembic e seed.

## Documentação

- Decisões novas → ADR em `docs/adr/` usando [`docs/adr/template.md`](docs/adr/template.md).
- Divergência entre docs e carta → comentário pro Michel, não correção silenciosa.
- Runbooks operacionais → `docs/runbooks/`.

## O que não fazer

- Secrets no repo (senhas, tokens, chaves).
- Bypass de RLS na aplicação em vez do banco.
- Merge de tabela de domínio sem checklist RLS.
- Scope creep fora da carta sem aprovação explícita.

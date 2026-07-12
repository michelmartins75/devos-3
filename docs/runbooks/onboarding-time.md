# Onboarding — Time Distribuído (DE / NL / BR)

Guia rápido para Daniel, André e novos membros entrarem no DevOS 3.0.

## 1. Acesso à rede (Tailscale)

1. Receber convite Tailscale da ForgeWorks.
2. Instalar o cliente Tailscale no seu sistema.
3. Autenticar com a conta autorizada.
4. Aguardar ACL aplicada no console Tailscale (CT130 ainda pendente de `tailscale up` — ver runbook).
5. Validar alcance a CT130 (`192.168.179.130`): portas **5432** (Postgres, readonly) e **8080** (API) — somente o permitido.

Detalhes de infra: [`ct130.md`](ct130.md) — não duplicar procedimentos de firewall/backup aqui.

## 2. Acesso ao repositório

1. Aceitar convite GitHub para `michelmartins75/devos-3` (privado).
2. Clonar: `git clone git@github.com:michelmartins75/devos-3.git`
3. Ler [`README.md`](../../README.md) e [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## 3. Ambiente local (opcional)

```bash
docker compose -f infra/docker-compose.yml up --build -d
# API: http://localhost:8080/health
# Console: http://localhost:3000
```

Para desenvolvimento Python: ver README → Quick start.

## 4. Primeiro PR

1. Abrir ou pegar uma issue com critérios de aceite.
2. Branch: `cursor/<descricao>-c7eb` ou branch de feature acordada.
3. **1 issue = 1 PR** — CI verde obrigatório.
4. Marcar revisor conforme área (ver CONTRIBUTING).
5. Se tocar tabela de domínio: checklist RLS em [`docs/design/rls-pattern.md`](../design/rls-pattern.md).

## 5. Quem aprova o quê

| Tipo de mudança | Aprovador |
|-----------------|-----------|
| Infra / CT130 | Michel (+ Codex como autor) |
| Código / migrações / CI | Michel ou Daniel |
| ADR / decisão arquitetural | Michel + Daniel |
| Docs de apoio | Michel |

## 6. Canais

- Dúvidas de escopo → carta de fundação (`docs/charter/`) ou Michel.
- Incidente CT130 → runbook [`ct130.md`](ct130.md).

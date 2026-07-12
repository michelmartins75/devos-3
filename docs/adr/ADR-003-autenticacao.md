# ADR-003: Autenticação e identidade

- **Status:** proposto
- **Dono:** Claude Code (OS-03)
- **Gateia:** auth F2.4 (Leva 2)

## Contexto

Decidir auth do DevOS 3.0: JWT próprio, OIDC genérico, ou Entra ID (EasyAuth) reaproveitado. Restrições: Azure permanente (D11), time distribuído via Tailscale (D8), `client_user` externos fora do Entra ForgeWorks, validação local-only sem dependência de nuvem.

## Decisão

_Pendente — conteúdo técnico vem do Claude Code (OS-03)._

## Consequências

_Pendente._

O middleware provisório `X-Tenant-ID` na API e no console web será substituído após este ADR.

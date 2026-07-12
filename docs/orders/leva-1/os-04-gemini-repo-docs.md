# OS-04 · Documentação de Nascença do Repo
**Ref.:** Carta de Fundação v1.2, tarefas G1–G3 · **Fase:** paralela · **Status:** entregue (2026-07-12)

## Missão
Fazer o repo `devos-3` ser navegável por um recém-chegado (humano ou agente) sem precisar perguntar nada a ninguém.

## Tarefas

### T1 — README raiz (PT-BR + EN) ✅
**Entregue:** [`README.md`](../../README.md) (PT-BR) + [`README.en.md`](../../README.en.md) (EN).

### T2 — CONTRIBUTING.md ✅
**Entregue:** [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — fluxo 1 issue = 1 PR, donos, commits, regra RLS.

### T3 — GLOSSARIO.md ✅
**Entregue:** [`GLOSSARIO.md`](../../GLOSSARIO.md) — termos da carta v1.2.

### T4 — Onboarding do time distribuído ✅
**Entregue:** [`docs/runbooks/onboarding-time.md`](../../runbooks/onboarding-time.md) — linka runbook CT130; nota Tailscale parcial conforme OS-01.

### T5 — Esqueletos de ADR ✅
**Entregue:**
- [`docs/adr/template.md`](../../adr/template.md)
- [`docs/adr/ADR-001-rls-isolamento.md`](../../adr/ADR-001-rls-isolamento.md)
- [`docs/adr/ADR-002-escalada-loop.md`](../../adr/ADR-002-escalada-loop.md)
- [`docs/adr/ADR-003-autenticacao.md`](../../adr/ADR-003-autenticacao.md)

## Aceite
- [x] T1–T3, T5 mergeados
- [x] T4 mergeado (com ressalva Tailscale pendente no CT130)
- [x] Prova prática: README aponta em <2 min onde rodar, decisões e revisores

## Fora de escopo
Conteúdo técnico de ADRs (OS-03), código de aplicação (OS-02), decisões novas.

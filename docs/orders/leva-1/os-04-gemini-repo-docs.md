# OS-04 · Gemini — Documentação de Nascença do Repo
**Ref.:** Carta de Fundação v1.2, tarefas G1–G3 · **Fase:** paralela, sem bloqueio

## Missão
Fazer o repo `devos-3` ser navegável por um recém-chegado (humano ou agente) sem precisar perguntar nada a ninguém. Tudo via PR.

## Tarefas

### T1 — README raiz (PT-BR + EN)
O que é o DevOS 3.0 (2 parágrafos, extraídos do sumário executivo da carta — não reescrever a visão, apontar pra ela), mapa da estrutura de pastas, como rodar localmente (link pro que o Cursor entregar na OS-02), onde estão as decisões (`docs/adr/`) e a fonte da verdade (`docs/charter/`).

### T2 — CONTRIBUTING.md
Fluxo de trabalho: 1 issue = 1 PR, branch protection, CI obrigatório, o dono da área como revisor (tabela de donos = §3 da carta), convenção de commits, e a regra: **nenhum merge em tabela de domínio sem o checklist RLS** (`docs/design/rls-pattern.md`, entregue pelo Cursor).

### T3 — GLOSSARIO.md
Termos do projeto com definição de 1–2 linhas cada: tenant, classe de tenant (`own`/`client`), Motor, pinning, SSOT, RLS, teste sagrado, loop interno/externo, preset de inferência (`local_only`/`eu_cloud`/`unrestricted`), capacidade (`reasoning`/`code_gen`/`embedding`/`triage`), registro de modelos, leva. Fonte: carta v1.2. Em dúvida, perguntar — não inventar definição.

### T4 — Onboarding do time distribuído (⚠ depende da OS-01/T7)
`docs/runbooks/onboarding-time.md`: como Daniel/André entram — Tailscale (resumir do runbook do Codex, não duplicar: linkar), acesso ao repo, primeiro PR, quem aprova o quê. Máximo 1 página.

### T5 — Esqueletos de ADR
Criar `docs/adr/template.md` (contexto → opções → decisão → consequências → status) e os stubs numerados ADR-001, ADR-002, ADR-003 com status `proposto`, título e dono — conteúdo técnico vem do Claude Code (OS-03), não desta OS.

## Aceite
- [ ] T1–T3, T5 mergeados
- [ ] T4 mergeado após entrega do runbook Tailscale (OS-01)
- [ ] Prova prática: uma pessoa que só leu o README acha em <2 min: onde rodar o projeto, onde estão as decisões, quem revisa o quê

## Fora de escopo
Conteúdo técnico de ADRs, código, qualquer decisão nova. Esta OS documenta o que a carta já decidiu — divergência encontrada entre docs vira comentário pro Michel, não correção silenciosa.

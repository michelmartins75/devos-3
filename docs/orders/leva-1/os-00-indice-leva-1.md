# DevOS 3.0 — Leva 1 (Estrutural) · Índice de Despacho
**Ref.:** Carta de Fundação v1.2 · **Data:** 2026-07-12 · **Orquestrador:** Michel

## Ordens desta leva

| OS | Agente | Objeto | Fase da carta |
|----|--------|--------|---------------|
| OS-01 | Codex | Infra CT130 → `devos-3-core` | Fase 0 |
| OS-02 | Cursor | Esqueleto do monorepo + fundação de tenancy (F1, F2.1–F2.2) | Fase 1 | **Entregue** |
| OS-03 | Claude Code | ADR-001 (revisão adversarial do modelo de dados) + ADR-003 (auth) | Paralela às Fases 0–1 |
| OS-04 | Gemini | Documentação de nascença do repo | Paralela | **Entregue** |

## Grafo de dependência

```
Pré-passo (Michel): criar repo `devos-3` + commitar carta em docs/charter/
        │
        ├── OS-01 (Codex) ──────────┐
        │                           │  ambiente pronto gateia deploy,
        ├── OS-02 (Cursor) ─────────┤  não gateia desenvolvimento
        │       │                   │
        │       └── migração 0002 (RLS) só mergeia após veredito ADR-001
        │                           │
        ├── OS-03 (Claude Code) ────┘
        │       └── ADR-003 gateia F2.4 (auth) da leva 2
        │
        └── OS-04 (Gemini) — sem bloqueio; onboarding Tailscale depende de saída da OS-01
```

**Regra de despacho:** OS-01, OS-02, OS-03 e OS-04 podem iniciar no mesmo dia. O único ponto de sincronização duro da leva: **a migração de RLS (OS-02, T5) não mergeia antes do veredito do ADR-001 (OS-03)**.

## O que a leva 1 NÃO contém (leva 2, só após gates desta)
Roteador de inferência/registro de modelos (F3), transplante de engines (F4), pinning de Motor (F5), migração v2→3.0 (F6), camada cliente (CC6/Fase 5).

## Critério de encerramento da leva 1
- Checklist da OS-01 100% (ambiente CT130 validado) — parcial (Tailscale ACL pendente)
- Teste sagrado de isolamento verde no CI (OS-02) — **entregue**
- ADR-001 e ADR-003 mergeados com decisão (OS-03)
- Repo navegável por um recém-chegado (OS-04) — **entregue**

Encerrada a leva 1, a leva 2 abre com F3 (registro de modelos) + F2.3 (SSOT de domínio) em paralelo.

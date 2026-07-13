# DevOS 3.0

DevOS 3.0 is the ForgeWorks Digital multi-tenant consolidation platform. It is a greenfield foundation, not a rewrite: tenancy, isolation, auditability, and inference policy are native from day one, while proven DevOS v2 capabilities are transplanted deliberately.

The source of truth for scope and decisions starts in `docs/charter/`. Operational runbooks live in `docs/runbooks/`, architecture decisions in `docs/adr/`, execution orders in `docs/orders/`, model-routing references in `docs/model-routing/`, and future design documents in `docs/design/`.

## Documentation Map

- `docs/charter/devos-3.0-carta-de-fundacao.md` - foundation charter and execution plan.
- `docs/orders/leva-1/` - Leva 1 dispatch index and OS-01 through OS-04.
- `docs/runbooks/ct130.md` - CT130 / `devos3` infrastructure runbook and OS-01 evidence.
- `docs/runbooks/hermes-infra.md` - local Hermes/Ollama runtime, MCP bridge, zero-egress boundary, and append-only audit evidence.
- `docs/model-routing/capabilities-matrix-template.md` - model capability matrix template for the orchestrator.
- `docs/model-routing/prompt-avaliacao-modelos-ia.md` - standardized model self-evaluation prompt.

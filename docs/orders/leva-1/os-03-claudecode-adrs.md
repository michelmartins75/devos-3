# OS-03 · Claude Code — ADRs de Fundação (Pensamento Profundo)
**Ref.:** Carta de Fundação v1.2, CC1 e CC3 · **Fase:** paralela às Fases 0–1

## Missão
Duas decisões arquiteturais que gateiam merges da leva 1 e 2: a revisão adversarial do modelo de isolamento (ADR-001) e a decisão de autenticação (ADR-003). Formato ADR padrão: contexto → opções → decisão → consequências, mergeado via PR em `docs/adr/`.

## Entrega 1 — ADR-001: Revisão adversarial do isolamento por RLS ★ gateia OS-02/T5

**Pergunta:** o desenho tenants + `app.tenant_id` + política `tenant_isolation` (USING/WITH CHECK) com `FORCE RLS` resiste a um atacante interno (bug de aplicação, dev descuidado, engine mal-portado)?

**Postura exigida: adversarial.** Não valide o desenho — tente quebrá-lo. Vetores mínimos a cobrir:
1. **Vazamento por contexto:** connection pooling reutilizando conexão com `app.tenant_id` sujo de request anterior; transação sem SET; `RESET`/`DISCARD` ausente. Recomendar mecanismo à prova de esquecimento (ex.: SET LOCAL por transação + middleware que falha fechado).
2. **Bypass por privilégio:** owner das tabelas, superuser, roles com `BYPASSRLS`; migração que esquece o FORCE. Recomendar checagem automatizada de postura (query de auditoria no CI que varre `pg_class`/`pg_policies`).
3. **Caminhos indiretos:** views (security_barrier?), funções `SECURITY DEFINER`, índices/EXPLAIN como canal lateral, `COPY`, FKs entre tenants (uma FK apontando pra linha de outro tenant deve ser impossível — como garantir?).
4. **Camada de fora do RLS:** sequences/IDs vazando cardinalidade, logs com dados de outro tenant, backups (o dump é multi-tenant — quem acessa?), `devos_readonly` do time externo (essa role vê tudo? deveria?).
5. **agent_jobs futuros:** o worker processa jobs de múltiplos tenants — o contexto por job proposto na OS-02 é suficiente ou precisa de conexão dedicada por tenant?

**Saída:** ADR-001 com veredito (aprova / aprova-com-mudanças / reprova o desenho), lista de mudanças obrigatórias pra OS-02/T5, e **casos de teste adicionais** pra suíte `isolation` (entregar como especificação que o Cursor implementa).

## Entrega 2 — ADR-003: Autenticação e identidade

**Pergunta:** auth do DevOS 3.0 — JWT próprio, OIDC genérico, ou Entra ID (EasyAuth) reaproveitado?

**Restrições do contexto (carta):** Azure é permanente (D11) e o v2 já usa Entra ID + EasyAuth; time distribuído DE/NL/BR entra por Tailscale (D8); futuros `client_user` são usuários de clientes externos que **não** estarão no tenant Entra da ForgeWorks; a política de inferência local-only (D4) não pode depender de ida à nuvem pra validar token em cenário de cliente soberano.

**Avaliar no mínimo:** (a) Entra ID pra time interno + provisão separada pra client_users; (b) OIDC self-hosted (Keycloak/Zitadel no CT130 — pesar custo operacional real); (c) JWT próprio minimalista com rotação de chaves. Considerar: service accounts dos agentes (Codex/Cursor/worker) com escopo mínimo, revogação, e o fato de auth ser superfície de ataque num produto cujo pitch é custódia segura.

**Saída:** ADR-003 com recomendação única e justificada + esboço do fluxo (humano interno, client_user, service account de agente). Gateia F2.4 na leva 2.

## Fora de escopo
Implementação de qualquer código (Cursor executa); ADR-002 (protocolo de escalada do loop — leva 2); threat model completo do CT130 (CC4, pré-go-live).

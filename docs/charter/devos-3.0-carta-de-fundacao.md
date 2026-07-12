# DevOS 3.0 — Carta de Fundação & Plano de Execução
### ForgeWorks Digital · De ferramenta single-project a plataforma multi-tenant de consolidação
**Versão:** 1.2 (D13: modelos parametrizáveis por tenant) · **Data:** 2026-07-12 · **Autores:** Michel Martins + Claude (arquiteto) · **Revisor:** Daniel Castro

---

## 0. Sumário Executivo

O DevOS v2 provou o pipeline (6 estágios, loop de validação, code-gen agêntico), mas nasceu single-tenant no osso. O DevOS 3.0 **não é um rewrite — é uma extração**: fundação greenfield com tenancy e isolamento nativos, transplantando do v2 a capacidade já provada (engines, padrão de loop, integração GitHub). O v2 segue vivo até a migração fechar.

**Premissa de produto:** o DevOS 3.0 é o motor de consolidação dos trabalhos de clientes E dos projetos próprios da ForgeWorks. O isolamento de tenant não é plumbing — **é a feature de manchete** ("teu código fica, teu dado é teu, DSGVO-by-design").

---

## 1. Registro de Decisões (cravadas nas sessões de co-design)

| # | Decisão | Consequência |
|---|---------|--------------|
| D1 | **Motor de base única** (não fork por tenant) | Exige versionamento/pinning de Motor por tenant; blast radius controlado por release gate |
| D2 | **Duas classes de tenant**: `own` (ForgeWorks) e `client` (externo) | Governança, residência de dado e roteamento de inferência divergem por classe |
| D3 | **Dois loops**: interno (validação executável, fecha sozinho) e externo (release do cliente, fecha com humano) | Rejeição interna alimenta DevOS; rejeição externa alimenta KnowledgeOS |
| D4 | **Política de inferência por tenant** (não bifurcação binária): preset default `client` → local-only (Terra); `own` → nuvem permitida; presets intermediários conforme país/regra do cliente | Upgrade do Terra gateia o 1º cliente externo *local-only*; clientes cuja regra permita nuvem EU não dependem do hardware |
| D5 | **Greenfield na fundação, transplante na capacidade** | Componente toca dado/identidade/isolamento → nasce novo. É lógica pura → porta do v2 |
| D6 | **Coexistência v2 ↔ 3.0** | Migração tenant a tenant; v2 como rede de segurança; sem big-bang |
| D7 | **SSOT do 3.0 nasce em PostgreSQL 16 + Row-Level Security no CT130** | Isolamento imposto no banco, não na aplicação; dado + inferência de tenant `client` no mesmo perímetro local |
| D8 | **Acesso time distribuído (DE/NL/BR) via Tailscale**, não via nuvem pública | Acesso ≠ nuvem; mesh VPN resolve Daniel/Holanda/André sem expor o SSOT |
| D9 | **Replit descartado do fluxo core**; uso restrito a protótipo pré-venda com dado sintético | Handoff via Template de Captura Pré-Venda → Spec Compiler |
| D10 | **Repo GitHub novo e independente** (`devos-3`), separado do Portalliz | Documentação nasce como código no repo desde o dia 1 |
| D11 | **Azure é infra permanente, não legado a descomissionar** | Portalliz produção, portal/EasyAuth, ACR e observabilidade seguem lá; modelo híbrido: SSOT 3.0 local + nuvem como braço de produto e dos tenants `own` |
| D12 | **Agentes por responsabilidade, não por exclusividade** | Codex pode codar, Cursor pode tocar infra, Grok entra onde convier; o que não flexibiliza: PR sempre, e D4 vale pra qualquer nuvem |
| D13 | **Modelos são conveniência parametrizável**: engines pedem *capacidade* (`reasoning`, `code_gen`, `embedding`, `triage`); registro de modelos + política do tenant resolvem *qual* modelo | Nenhum papel de modelo hardcoded no 3.0; a tabela de agentes (§3) é seed/configuração default, não arquitetura; regra do país do cliente entra como parâmetro do tenant |

**Decisões em aberto (não bloqueiam início):**
- OA1 (resolvida → D11): Azure permanece. Detalhe restante: auth do portal 3.0 (EasyAuth vs. próprio) sai do ADR-003.
- OA2: Semente de código Replit permitida em greenfield ou spec-only sempre? (política, Fase 4)
- OA3: Protocolo da camada cliente: CopilotKit/AG-UI vs. build próprio sobre MCP (Fase 5, pós-go-live)

---

## 2. Arquitetura Alvo

### 2.1 O que NASCE NOVO (fundação — obsessão do 3.0)
- **Modelo de dados tenant-aware**: toda tabela do SSOT carrega `tenant_id` desde a primeira migração; RLS impõe o isolamento no banco.
- **Identidade & RBAC**: papéis por tenant (owner, operator, client_user); service accounts por agente com escopo mínimo.
- **Registro de tenants**: classe (`own`/`client`), versão de Motor fixada (pinning), política de inferência, residência de dado.
- **Roteador de inferência**: decide local (Ollama/Terra) vs. nuvem (Gemini/CLIs) pela classe do tenant. Nativo, não enxertado.
- **Trilha de auditoria**: toda ação de agente logada com tenant, ator, custo e resultado (base pra billing por horas de assinatura).

### 2.2 O que se TRANSPLANTA do v2 (capacidade provada)
- Pipeline de 6 estágios (Use Case → Requirement → Spec → Sprint → Development → Validation → Documentation).
- Engines: orchestrator, requirement-engine, spec-engine, development-engine, validation-engine, documentation-engine.
- Padrão de loop do validador (CT172): devolver o que não é válido contra o requisito → agora com teto de iterações e escalada.
- Integração GitHub (Branch + PR, barramento de artefatos) e o modelo PULL (worker local puxa jobs).
- Prompts, spec compiler e aprendizados acumulados dos engines.

### 2.3 O que NÃO entra no 3.0 v1 (escopo cortado deliberadamente)
- Camada self-service do cliente: *construção* na Fase 5 — mas o *design* (CC6) roda em paralelo às Fases 3–4. Fora do go-live, dentro da estratégia.
- Substrato meta-driven completo → evolução contínua.
- Loop apontado pra cliente externo → gateado por D4 (hardware Terra) + Fundação completa.

### 2.4 Topologia física

```
Proxmox Principal (.67)
└── CT130 (reciclado) — "devos-3-core"
    ├── PostgreSQL 16 (SSOT, RLS por tenant)
    ├── API DevOS 3.0 (FastAPI) + Orchestrator/AgentOS
    ├── Worker (Agent Runner) — executa CLIs por assinatura
    └── Tailscale (subnet router p/ time DE/NL/BR)

Terra (.128) — inferência local
└── CT100 Ollama (.133) — qwen3:32b, qwen3-coder:30b, llama3.2:3b, nomic-embed-text

GitHub — repo novo `devos-3` (código + docs + ADRs)
Azure — infra permanente (D11): Portalliz produção, portal/EasyAuth, ACR, observabilidade; braço de nuvem dos tenants `own`. O SQL do v2 sai de cena só quando a migração fechar
```

---

## 3. Papéis dos Agentes (a equipe de execução)

| Agente | Papel | Responsabilidade | Modelo de handoff |
|--------|-------|------------------|-------------------|
| **Codex** | Gerente de Infra | Prepara CT130: SO, Docker, Postgres, rede, hardening, backups | Recebe a **Spec de Infra (§4)**; entrega ambiente validado pelo checklist §4.6 |
| **Cursor** | Desenvolvedor | Código, testes, migrações, CI | Recebe o **Backlog (§5)** como issues no GitHub; PR por tarefa; critérios de aceite executáveis |
| **Claude Code** | Pensamento profundo | Tarefas de arquitetura que exigem raciocínio longo (§6) | Recebe contexto do repo + ADR alvo; entrega ADR/design doc/revisão |
| **Gemini** | Tarefas gerais | Documentação de apoio, resumos, traduções, formatação (§7) | Tarefas sem exigência de modelo de código/infra |
| **Grok** | Reforço flexível | Entra onde for conveniente (código, análise, pesquisa) a critério do orquestrador humano | Mesmo regime de PR; sujeito a D4 como qualquer nuvem |
| **Ollama (Terra)** | Inferência local | Validação de requisito no loop, embeddings do KnowledgeOS, triagem | Consumido pela API via roteador de inferência |

**Modelo de responsabilidade, não de exclusividade (D12):** os papéis acima definem quem é *dono* de cada área — não quem pode tocá-la. Codex pode escrever código, Cursor pode ajustar infra, Grok entra onde convier; o roteamento é por capacidade e disponibilidade, a critério do orquestrador humano. Dois pontos não flexibilizam: (1) tudo passa por PR no `devos-3`, com o dono da área como revisor; (2) **D4 vale pra qualquer modelo de nuvem — Grok incluído**: contexto de tenant `client` sob preset `local_only` nunca sai do perímetro local, independente de quão conveniente o modelo seja.

**E os papéis viram parâmetro (D13):** esta tabela é a *configuração default* que alimenta o registro de modelos (F3.1) como seed — não arquitetura. Por tenant, conforme país e regra do cliente, o mapeamento capacidade→modelo se ajusta em dado, sem tocar em código.

---

## 4. SPEC DE INFRA — Ordem de serviço pro Codex

> **Objetivo:** transformar o CT130 (descontinuado) no `devos-3-core`, pronto pra receber a aplicação com segurança de nível "custódia de código de cliente".

### 4.1 Container LXC (Proxmox Principal .67)
- Destruir CT130 antigo após snapshot de segurança do host.
- Recriar CT130: **Debian 12**, unprivileged, nesting=1 (p/ Docker).
- Recursos iniciais: **4 vCPU, 8 GB RAM, 60 GB disco** (local-lvm). *Atenção: host já carrega 13 apps — validar folga antes com `pct list` + `free -h` no host; se apertado, propor realocação, não improvisar.*
- Hostname: `devos3`. IP estático: **192.168.178.130** (reaproveita o .130 do Ollama antigo — CONFIRMAR que a migração pro .133 está concluída e o .130 está livre; consta "a aposentar" no schema).

### 4.2 Base do sistema
- Docker Engine + Compose plugin.
- UFW: default deny incoming; allow 22 (só da LAN), 5432 (só Tailscale + localhost), 8080 (API, só LAN + Tailscale).
- fail2ban no SSH; SSH por chave, root login off.
- Unattended-upgrades (security only).

### 4.3 PostgreSQL 16 (o SSOT)
- Container Docker oficial `postgres:16`, volume dedicado, `listen_addresses` restrito.
- Databases: `devos_app` (SSOT) e `devos_audit` (trilha, WORM-like: sem DELETE grant).
- Usuários: `devos_api` (aplicação, sujeito a RLS), `devos_migrator` (DDL, uso só em migração), `devos_readonly` (relatórios).
- **RLS habilitado por padrão em toda tabela de domínio** — a política é entregue pelo Cursor nas migrações, mas o Codex garante que `FORCE ROW LEVEL SECURITY` é o padrão do template de criação.
- Backup: `pg_dump` diário → NAS/segundo disco + retenção 14d; teste de restore mensal agendado.

### 4.4 Rede do time distribuído
- Tailscale no CT130 como subnet router (ou node simples se preferir por-serviço).
- ACL Tailscale: Daniel (NL), André (BR) → apenas portas 5432 (via usuário `devos_readonly` ou role dev) e 8080. Nada de acesso ao host Proxmox.
- Documentar no repo: onboarding de um novo membro na rede em ≤ 10 passos.

### 4.5 Ponte de inferência
- Testar alcance CT130 → `ollama.lan` (.133) porta 11434; latência de baseline documentada.
- Variáveis de ambiente padrão: `INFERENCE_LOCAL_URL`, `INFERENCE_CLOUD_KEYS` (via secrets, nunca em compose).

### 4.6 Checklist de aceite do ambiente (gate da Fase 0)
- [ ] CT130 recriado, snapshot pós-setup tirado
- [ ] Postgres up, RLS default confirmado com teste de duas roles
- [ ] Backup executado E restaurado com sucesso uma vez
- [ ] Tailscale: Daniel e André alcançam API e banco conforme ACL, e NADA além
- [ ] UFW auditado (`ufw status verbose` documentado no repo)
- [ ] Ping de inferência CT130 → Terra ok, baseline registrada
- [ ] Runbook `docs/runbooks/ct130.md` commitado

---

## 5. BACKLOG DE DESENVOLVIMENTO — Ordem de serviço pro Cursor

> Cada épico vira milestone no GitHub; cada tarefa vira issue com os critérios de aceite como checklist. PR por tarefa, review humano (Michel/Daniel) até o loop de validação estar confiável.

### Épico F1 — Esqueleto & CI (Fase 1)
- **F1.1** Monorepo `devos-3`: `apps/api`, `apps/worker`, `packages/shared-types`, `packages/engines/*`, `infra/`, `docs/`.
- **F1.2** FastAPI + healthcheck + estrutura de config por ambiente. *Aceite: `/health` = 200 no CT130.*
- **F1.3** CI GitHub Actions: lint + testes + build em todo PR. *Aceite: PR sem CI verde não mergeia (branch protection).*
- **F1.4** Migrações com Alembic; migração 0001 cria `tenants`, `users`, `memberships`. *Aceite: rollback testado.*

### Épico F2 — Fundação de Tenancy (Fase 1–2) ★ o coração
- **F2.1** Tabela `tenants`: `id, name, class(own|client), motor_version, inference_policy (preset F3.3), data_residency, status`.
- **F2.2** RLS: política `tenant_isolation` em toda tabela de domínio; contexto via `SET app.tenant_id`. *Aceite: teste automatizado prova que a role da API com tenant A não lê NENHUMA linha do tenant B — este teste é sagrado e roda em todo CI.*
- **F2.3** SSOT de domínio: `work_items`, `requirements`, `specs`, `sprints`, `agent_jobs`, `validations`, `changelog`, `traceability` — todas com `tenant_id NOT NULL` + FK + RLS.
- **F2.4** Auth: JWT próprio ou OIDC (decidir com ADR-003); RBAC owner/operator/client_user por tenant.
- **F2.5** Trilha de auditoria: middleware que grava ator, tenant, ação, custo estimado em `devos_audit`. *Aceite: nenhuma rota de escrita sem entrada de auditoria.*

### Épico F3 — Registro de Modelos & Roteador de Inferência (Fase 2) ★ D13
- **F3.1** Tabela `models`: `id, provider, endpoint, capabilities[], residency (região/local de processamento), data_processing_terms, cost_class, status`. Ollama (Terra), Gemini, Claude, Codex, Cursor e Grok entram como **linhas do registro**, não como código. Seed inicial = tabela de agentes da §3.
- **F3.2** Interface por capacidade: engines pedem `reasoning | code_gen | embedding | triage` — nunca um modelo nomeado. *Aceite: nenhum engine importa cliente de provider diretamente; teste de arquitetura falha se importar.*
- **F3.3** Política por tenant (`tenant_model_policies`): allowlist/denylist de providers, exigência de residência, teto de custo. Presets nomeados: `local_only` (default classe `client`), `eu_cloud`, `unrestricted` (default classe `own`). País/regra do cliente seleciona o preset e o refina.
- **F3.4** Violação de política → **erro hard + entrada de auditoria**, nunca fallback silencioso pra modelo conveniente. *Aceite: teste cobre tentativa de rota cloud num tenant `local_only`.*
- **F3.5** Métricas: latência, tokens e custo por chamada, por tenant e por modelo — insumo do billing por horas e da própria decisão de conveniência (dados dizem qual modelo rende onde).

### Épico F4 — Transplante dos Engines (Fase 2–3)
- **F4.1** Portar `shared-types`, `github-client`, `storage-client` do v2, adaptando ao SSOT novo.
- **F4.2** Portar orchestrator + requirement-engine + spec-engine (tenant-aware via contexto, sem lógica de tenant dentro do engine).
- **F4.3** Portar development-engine + worker (modelo PULL preservado; `agent_jobs` com `tenant_id`).
- **F4.4** Portar validation-engine com o padrão CT172 **+ upgrades do loop**: teto de N iterações, orçamento por job, e três rotas de escalada (humano / mudança-de-Motor / requisito-inconstruível). *Aceite: caso de teste de não-convergência termina em escalada, nunca em loop infinito.*
- **F4.5** Portar documentation-engine.

### Épico F5 — Pinning de Motor & Release Gate (Fase 3)
- **F5.1** Versionamento semântico do Motor; `tenants.motor_version` respeitado pelo orchestrator.
- **F5.2** Fluxo de promoção: Motor novo roda primeiro em tenant `own` designado (canário) → aprovação humana → promove por tenant. *Aceite: dois tenants rodando versões diferentes de Motor simultaneamente, com sucesso, em teste de integração.*

### Épico F6 — Migração & Coexistência (Fase 4)
- **F6.1** Importador v2 → 3.0 (Azure SQL → Postgres) por projeto: Portalliz primeiro (piloto), depois zev-lur, depois NAU.
- **F6.2** Período de sombra: projeto roda nos dois; divergências documentadas.
- **F6.3** Critério de desligamento do v2 por projeto. Azure não se descomissiona (D11): o SQL do v2 sai de cena quando a migração fechar; Container Apps, ACR, EasyAuth e observabilidade seguem permanentes.

---

## 6. TAREFAS CLAUDE CODE — pensamento profundo

| ID | Tarefa | Entregável |
|----|--------|-----------|
| CC1 | **ADR-001**: revisão adversarial do modelo de dados tenant-aware (F2.3) — caçar toda rota de vazamento entre tenants (joins, views, funções, índices, EXPLAIN bypass) | ADR + suíte de testes de isolamento adicionais |
| CC2 | **ADR-002**: desenho do protocolo de escalada do loop (F4.4) — taxonomia de não-convergência e política de orçamento | ADR + máquina de estados do job |
| CC3 | **ADR-003**: decisão de auth (JWT próprio vs OIDC vs manter Entra só pro portal) considerando OA1 | ADR com recomendação |
| CC4 | Revisão de segurança pré-go-live: threat model do CT130 + API (STRIDE leve), com foco em "custódia de código de cliente" | Relatório + issues de correção |
| CC5 | Desenho da **fábrica de evals** do KnowledgeOS — antecipado: roda em paralelo às Fases 2–3, porque a camada cliente depende dele | Design doc `docs/design/eval-factory.md` |
| CC6 | Desenho da **camada cliente** (captura de intenção in-app, aterramento via MCP, classificador de triagem config/campo/módulo) — em paralelo às Fases 3–4, pra Fase 5 começar *construindo*, não desenhando | Design doc `docs/design/camada-cliente.md` |

## 7. TAREFAS GEMINI — apoio geral

- G1: README, CONTRIBUTING e glossário do repo `devos-3` (PT-BR + EN).
- G2: Converter as decisões deste documento em ADRs formatados (esqueleto; conteúdo técnico vem de CC/humano).
- G3: Onboarding doc do time distribuído (Tailscale, acesso, fluxo de PR).
- G4: Changelog e release notes a cada fase.
- G5: Tradução/resumo de documentação técnica de terceiros quando necessário.

## 8. Ollama / Terra — arsenal e pedidos

**Já disponível e suficiente pro go-live:** `qwen3:32b` (raciocínio/validação), `qwen3-coder:30b` (análise de código no loop), `llama3.2:3b` (triagem rápida/barata), `nomic-embed-text` (embeddings do KnowledgeOS).

**Pedido de novos modelos: nenhum agora.** Motivo: com 24 GB de VRAM, um modelo grande por vez — disciplina de uso vale mais que variedade. Reavaliar quando: (a) 2ª GPU instalada, ou (b) a fábrica de evals (CC5) exigir um modelo de raciocínio dedicado. Aí sim, candidato natural: um reasoning model compacto pra rodar residente ao lado do coder.

---

## 9. Repo GitHub `devos-3` — estrutura de nascença

```
devos-3/
├── docs/
│   ├── charter/          ← ESTE documento (fonte da verdade)
│   ├── adr/              ← ADR-001..N (decisões arquiteturais)
│   ├── design/           ← eval-factory, camada-cliente (futuro)
│   ├── runbooks/         ← ct130, backup-restore, onboarding-tailscale
│   └── migration/        ← plano e log da migração v2→3.0
├── apps/{api,worker}/
├── packages/{shared-types,engines/*}/
├── infra/                ← compose, provisionamento, políticas UFW/Tailscale (sem secrets)
└── .github/workflows/
```

Owner: michelmartins75 · **Separado do Portalliz** · Privado · Branch protection na `main` desde o dia 1.

---

## 10. Fases até o Go-Live

| Fase | Nome | Conteúdo | Gate de saída | Responsável primário |
|------|------|----------|---------------|---------------------|
| **0** | Ambiente | Spec §4 completa no CT130 | Checklist §4.6 100% | Codex |
| **1** | Esqueleto | F1 + F2.1–F2.2 | Teste sagrado de isolamento verde no CI | Cursor |
| **2** | Fundação | F2.3–F2.5 + F3 + início F4 | RLS em todo domínio; roteador bloqueando cloud p/ `client` | Cursor + CC1/CC2/CC3 |
| **3** | Capacidade | F4 completo + F5 | Pipeline de 6 estágios roda ponta-a-ponta num tenant `own` de teste; dois Motores coexistindo | Cursor |
| **4** | Migração piloto | F6.1–F6.2 com Portalliz | Portalliz 100% no 3.0, v2 em sombra, zero divergência por 2 semanas | Cursor + Michel |
| **GO-LIVE** | 3.0 oficial | Portalliz promovido; zev-lur e NAU na fila | CC4 (security review) sem issue crítico aberto | Michel + Daniel |
| **5** | Camada Cliente (estratégica) | Construção da camada de captura de intenção (sobre CC5+CC6 já prontos) + fábrica de evals + migração restante e desligamento v2 | Camada cliente pilotando num tenant `own` (dogfood) — apontar pra cliente externo segue gateado por D4 | todos |

**Definição de Go-Live:** o DevOS 3.0 é o sistema de registro e execução de pelo menos um tenant real (Portalliz), com isolamento provado por teste, auditoria ativa, backup testado e v2 ainda disponível como contingência.

**O que o go-live NÃO exige (pra não inflar escopo):** cliente externo, upgrade do Terra, meta-driven completo. **A camada cliente muda de status:** o design dela (CC5 + CC6) roda em paralelo às Fases 2–4, e a Fase 5 começa construindo — ela é estratégia com data, não backlog. O que segue gateado por D4 é apenas apontá-la pra cliente *externo*.

---

## 11. Riscos & Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Vazamento entre tenants | Existencial (legal + reputação) | RLS no banco + teste sagrado no CI + CC1 adversarial + CC4 pré-go-live |
| Host .67 sobrecarregado (13 apps + CT130) | Degradação geral | Medição antes (§4.1); realocação planejada, não improviso |
| Rewrite scope creep ("já que é do zero…") | Cronograma | Escopo §2.3 cortado por escrito; toda adição = mudança de charter aprovada |
| Fadiga de coexistência (manter v2 + 3.0) | Desgaste do time | Migração por projeto com critério de desligamento explícito (F6.3) |
| Loop sem convergência queimando recursos | Custo/paralisia | Teto + orçamento + escalada (F4.4/CC2), aceite testado |
| IP .130 ainda em uso pelo Ollama legado | Conflito de rede | Verificação obrigatória na §4.1 antes de atribuir |
| Dependência de um humano (Michel) como gate único | Bus factor | Daniel como segundo aprovador de release de Motor desde a Fase 3 |

---

*ForgeWorks Digital — o código fica conosco, a licença vai ao cliente. Dados nunca saem da UE.*

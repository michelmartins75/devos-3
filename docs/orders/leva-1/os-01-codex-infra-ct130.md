# OS-01 · Codex — Infraestrutura CT130 → `devos-3-core`
**Ref.:** Carta de Fundação v1.2, §4 · **Papel:** dono da infra (D12) · **Fase:** 0

## Missão
Transformar o CT130 (descontinuado) no host da fundação do DevOS 3.0: Debian 12 + Docker + PostgreSQL 16 endurecido + Tailscale, pronto pra custódia de código de cliente. Ambiente entregue = checklist §6 desta OS 100% verde, com evidência.

## Contexto mínimo necessário
- Host: Proxmox Principal `.67` (192.168.178.0/24), já carrega 13 apps em produção — **cautela é requisito**.
- Inferência local: Ollama em `ollama.lan` → 192.168.178.133 (host Terra), porta 11434.
- Time distribuído que precisará de acesso: Daniel (NL), André (BR), Michel (DE).
- O SSOT do DevOS 3.0 morará neste CT (PostgreSQL 16 com RLS). Isolamento de tenant é a feature de manchete do produto — trate o banco como subsistema crítico de segurança.

## Pré-verificações obrigatórias (parar e reportar se falhar)
1. **Capacidade do host:** coletar `pct list`, `free -h`, `df -h` e carga média no `.67`. Se a folga para 4 vCPU / 8 GB RAM / 60 GB disco não existir com margem, **não improvisar** — reportar com números e propor realocação.
2. **IP 192.168.178.130 livre:** o schema marca o Ollama legado no `.130` como "a aposentar". Confirmar que nada responde (ping, arp, port scan básico) e que nenhum serviço aponta pra ele. Colisão de IP aqui morde silencioso.
3. **Snapshot/backup do estado atual do CT130** antes de destruir, mesmo descontinuado.

## Tarefas

### T1 — Container
- Destruir CT130 antigo (após snapshot). Recriar: **Debian 12, unprivileged, nesting=1**.
- Recursos: 4 vCPU, 8 GB RAM, 60 GB (local-lvm). Hostname `devos3`, IP estático `192.168.178.130`.
- Snapshot pós-setup básico.

### T2 — Base e hardening
- Docker Engine + Compose plugin.
- UFW: default deny incoming; allow 22 (só LAN), 5432 (só localhost + interface Tailscale), 8080 (LAN + Tailscale).
- SSH: só chave, root login off, fail2ban ativo.
- unattended-upgrades (security only).

### T3 — PostgreSQL 16 (o SSOT)
- Container `postgres:16` oficial, volume dedicado, `listen_addresses` restrito (localhost + IP Tailscale).
- Databases: `devos_app` e `devos_audit` (auditoria: role da aplicação **sem grant de DELETE/UPDATE** — trilha é append-only).
- Roles: `devos_api` (aplicação, sujeita a RLS — **NUNCA superuser, NUNCA owner das tabelas**), `devos_migrator` (DDL, só migração), `devos_readonly` (relatórios/time externo).
- Garantir no template/padrão do projeto: tabelas de domínio nascem com `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY`. As políticas em si chegam via migrações do Cursor (OS-02); tua entrega é o banco recusar acesso sem política.
- Secrets via arquivo `.env` fora do repo + permissões 600. **Nenhuma senha em compose commitado.**

### T4 — Backup com prova
- `pg_dump` diário (cron) → segundo destino (NAS/disco separado), retenção 14 dias.
- **Executar um ciclo completo backup → restore em database de teste e documentar.** Backup sem restore provado não conta como backup.

### T5 — Tailscale (acesso DE/NL/BR)
- Instalar no CT130. ACL: Daniel e André alcançam **somente** 5432 e 8080 deste host. Zero acesso ao Proxmox host ou a outros CTs.
- Testar de fora da LAN (ou simular) e registrar evidência.

### T6 — Ponte de inferência
- Do CT130, validar alcance a `ollama.lan:11434` (usar endpoint `/api/tags`). Registrar latência de baseline.

### T7 — Runbook
- Entregar `docs/runbooks/ct130.md` no repo `devos-3` via PR: como recriar o ambiente do zero, onde estão os secrets (referência, não valor), como rodar backup/restore, como auditar o firewall, como adicionar membro no Tailscale em ≤ 10 passos.

## Checklist de aceite (gate da Fase 0)
- [ ] Pré-verificações 1–3 reportadas com evidência
- [ ] CT130 recriado conforme T1, snapshot tirado
- [ ] `ufw status verbose` documentado; portas conferem com T2
- [ ] Postgres up; teste com duas roles prova que tabela com RLS sem política **recusa** leitura pra `devos_api`
- [ ] Ciclo backup→restore executado e documentado
- [ ] ACL Tailscale testada: membros alcançam o permitido e NADA além
- [ ] Baseline de latência CT130→Ollama registrada
- [ ] Runbook mergeado no repo

## Fora de escopo (não fazer)
- Qualquer código de aplicação, schema de domínio ou política RLS específica (Cursor, OS-02).
- Tocar em qualquer outro CT/VM do host `.67` ou do Terra.
- Expor qualquer porta pra internet pública.
- Decidir auth da aplicação (ADR-003, OS-03).

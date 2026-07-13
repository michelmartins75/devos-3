# Hermes Local Infrastructure Runbook

Date: 2026-07-13  
Scope: DevOS 3.0 local inference, Hermes Agent runtime, CT172 MCP bridge, and PostgreSQL audit trail.

## Status

The environment is operational on the local Proxmox network. Tailscale onboarding and production ACLs remain intentionally pending. Until then, equivalent source-IP allowlists enforce the service boundary on the LAN.

No application source code was changed during this work.

## Topology

| Component | Host | Guest | Address | Purpose |
|---|---|---|---|---|
| Ollama / GPU | Terra Proxmox `192.168.179.128` | CT100 `ct-ai` | `192.168.179.231:11434` | Local OpenAI-compatible inference |
| Hermes Agent | Terra Proxmox `192.168.179.128` | CT110 `hermes-agent` | `192.168.179.233` | Agent runtime and hardened tool sandbox |
| DevOS PostgreSQL 16 | Thomas Proxmox `192.168.179.67` | CT130 `devos3` | `192.168.179.130:5432` | SSOT and Hermes audit storage |
| CT172 Auditor | Thomas Proxmox `192.168.179.67` | CT172 | `192.168.179.218:4200` | Independent validation service exposed to Hermes through MCP |

Service flow:

```text
Hermes Agent (CT110)
  |-- Ollama API --> CT100:11434
  |-- MCP stdio bridge --> CT172:4200
  `-- append-only audit --> CT130:5432
```

## Ollama and model

Ollama runs as a restartable service on CT100 with the Tesla P40 passed through.

Effective Hermes model:

- Tag: `hf.co/NousResearch/Hermes-4.3-36B-GGUF:Q3_K_M`
- Context configured in Hermes Agent: 65,536 tokens
- GPU: NVIDIA Tesla P40, 23,040 MiB reported
- Observed under model load: approximately 21.6 GiB VRAM plus host RAM
- Observed offload: approximately 52% CPU / 48% GPU
- Observed generation rate: approximately 2.4 tokens/second

The original target of 36B Q4_K_M at 128K could not be met safely on one P40. The Q4 build fell back to CPU, while the 14B build fit entirely in VRAM but did not provide the minimum context required by Hermes Agent. Q3_K_M at 65,536 is the validated operating point.

Network exposure:

- CT100 permits TCP 11434 from CT110.
- The existing DevOS CT130 Ollama rule remains documented in the CT130 runbook.
- The endpoint is not intended for public exposure.

## Hermes Agent runtime

CT110 characteristics:

- Ubuntu 24.04 LXC
- unprivileged container
- 4 vCPU
- 8 GiB RAM
- 32 GiB disk
- Hermes Agent 0.18.2
- Docker terminal backend

Provider configuration:

- provider abstraction: custom OpenAI-compatible endpoint
- base URL: `http://192.168.179.231:11434/v1`
- default model: Hermes 4.3 36B Q3_K_M
- context: 65,536
- default maximum output: 512
- fallback providers: configured as an empty list and disabled by default

Tool sandbox controls validated:

- Docker network mode: none
- privileged mode: false
- all Linux capabilities dropped
- `no-new-privileges` enabled
- PID limit: 256
- CPU limit: 2
- memory limit: 4 GiB
- tool calls cannot reach the CT110 host or external networks through the sandbox

## Tenant zero-egress boundary

CT110 has a persistent `HERMES_EGRESS` output chain. It permits only:

- loopback
- established and related responses
- `192.168.179.231:11434/tcp` — Ollama
- `192.168.179.218:4200/tcp` — CT172
- `192.168.179.130:5432/tcp` — PostgreSQL

All other CT110 output is rejected.

Validation evidence:

- Ollama from CT110: allowed
- CT172 health from CT110: allowed
- PostgreSQL append-only insert from CT110: allowed
- external HTTPS probe to `1.1.1.1:443`: blocked
- Docker tool sandbox network probe: blocked

The systemd unit is `hermes-tenant-egress.service`.

## CT172 MCP bridge

Hermes Agent registers CT172 as an MCP stdio server. The local bridge translates MCP tools to the existing Fastify API without modifying CT172 application code.

Tools discovered:

- `ct172_health`
- `ct172_validate`

Validated MCP response from `ct172_health`:

- `status: ok`
- Ollama reachable
- repository accessible
- MCP error: false

The MCP client and server discovery/call path passed before and after the CT110 egress allowlist was enabled.

Known runtime limitation:

A model-directed MCP call loaded a tool context larger than the effective model window and stopped before tool selection. Direct MCP discovery and invocation from the Hermes runtime pass. Before enabling large skill/gateway bundles, reduce the tool schema loaded into each run or select MCP tools explicitly.

## PostgreSQL audit trail

PostgreSQL 16 runs in container `devos3-postgres` on CT130.

Schema and table:

- schema: `audit`
- table: `audit.hermes_events`

Minimum event fields:

- `tenant_id`
- `run_id`
- `provider`
- `model`
- `subagent`
- `tool`
- `ct172_verdict`
- `timestamp`
- `egress_flag`
- `metadata`

Indexes cover tenant/timestamp, run ID, and timestamp retention scans.

Append-only identities:

- Hermes Agent has a dedicated writer role.
- CT172 has a separate dedicated writer role.
- Both roles have `INSERT` and identity-sequence usage.
- Both roles are denied `SELECT`, `UPDATE`, `DELETE`, and `TRUNCATE`.
- Credentials are stored only on the respective containers with restrictive filesystem permissions.

Do not commit database passwords or the environment files.

Network controls:

- PostgreSQL publishes on `192.168.179.130:5432`.
- The `DOCKER-USER` chain permits only CT110 (`192.168.179.233`) and CT172 (`192.168.179.218`) to reach port 5432.
- A connection probe from CT140 was blocked.

Retention:

- Events older than 180 days are deleted by `hermes-audit-retention.timer`.
- The timer runs daily with randomized delay.
- Retention runs with the database administrator identity; append-only writer roles cannot delete records.

## Acceptance evidence

Validated successfully:

- local Hermes chat through Ollama
- Hermes Agent file tool call in the Docker sandbox
- sandbox isolation and no network
- MCP discovery of two CT172 tools
- MCP `ct172_health` call returning a healthy result
- append-only insert from Hermes Agent
- append-only insert from CT172
- failed `SELECT` and `UPDATE` attempts for both writer roles
- audit event for `ct172_health` with `egress_flag = false`
- external egress blocked from CT110
- unauthorized PostgreSQL source blocked

Representative audited run:

- tenant: `local-smoke`
- provider: `custom`
- model: Hermes 4.3 36B Q3_K_M
- tool: `ct172_health`
- verdict status: `ok`
- egress flag: `false`

## Security exception and pending work

### CT172 GitHub identity

The CT172 independence hard gate was explicitly waived for this provisioning pass. CT172 currently has a GitHub credential broader than the desired read-only validation profile.

Before production:

1. Create a dedicated CT172 GitHub identity or GitHub App.
2. Restrict it to repository read and pull-request metadata required by validation.
3. Remove push, workflow, administration, and deployment capabilities.
4. Rotate the existing credential.
5. Re-run `ct172_validate` against a disposable PR and document the resulting verdict.

Never place the current credential or its value in this repository.

### Tailscale

Tailscale remains pending until production onboarding. Before replacing the temporary LAN rules:

1. Authenticate CT100, CT110, CT130, and CT172 into the intended tailnet.
2. Assign stable tags/identities.
3. Define least-privilege ACLs for the same three CT110 flows.
4. Bind or publish Ollama and PostgreSQL only on the intended Tailscale path.
5. Validate allowed flows and prove that all other tailnet and Internet flows fail.
6. Update this runbook with Tailscale addresses and ACL references.

## Operational checks

On Terra:

```bash
pct status 100
pct status 110
pct exec 100 -- ollama list
pct exec 100 -- nvidia-smi
pct exec 110 -- systemctl status docker hermes-tenant-egress.service
pct exec 110 -- iptables -S HERMES_EGRESS
```

On Thomas:

```bash
pct status 130
pct status 172
pct exec 172 -- curl -fsS http://127.0.0.1:4200/health
pct exec 130 -- docker exec devos3-postgres pg_isready -U postgres -d postgres
pct exec 130 -- systemctl status hermes-audit-firewall.service
pct exec 130 -- systemctl status hermes-audit-retention.timer
pct exec 130 -- iptables -S DOCKER-USER
```

## Maintenance notes

- Monitor the Terra `ssd-ai` thin pool; it was approximately 81% allocated during provisioning.
- A CT100 snapshot can retain model-storage blocks and delay space reclamation.
- Do not enable cloud fallback for tenant-local runs.
- Do not add MCP/skill bundles until their combined prompt and tool schema fit the effective context window.
- Revalidate GPU offload and generation rate after model, Ollama, or driver upgrades.

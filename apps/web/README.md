# DevOS 3.0 — Web Console

Operator console (Leva 1 shell): dashboard, API health, provisional tenant context.

## Development

```bash
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:3000 — API expected at `VITE_API_URL` (default `http://localhost:8080`).

## Production build

```bash
npm run build
npm run preview
```

Or via Docker / `infra/docker-compose.yml` (`web` service on port 3000).

## Scope

This is **not** the client-facing layer (Fase 5 / CC6). Auth is provisional via `X-Tenant-ID` until ADR-003.

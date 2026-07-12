import { useCallback, useEffect, useState } from "react";

import { fetchHealth, fetchStatus, type StatusResponse } from "./api/client";

const TENANT_STORAGE_KEY = "devos3.tenant_id";

export function App() {
  const [tenantId, setTenantId] = useState(
    () => localStorage.getItem(TENANT_STORAGE_KEY) ?? "",
  );
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    const context = tenantId.trim() || null;
    try {
      await fetchHealth(context);
      const payload = await fetchStatus(context);
      setStatus(payload);
    } catch (err) {
      setStatus(null);
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (tenantId.trim()) {
      localStorage.setItem(TENANT_STORAGE_KEY, tenantId.trim());
    } else {
      localStorage.removeItem(TENANT_STORAGE_KEY);
    }
  }, [tenantId]);

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">D3</span>
          <div>
            <strong>DevOS 3.0</strong>
            <p>Console operacional</p>
          </div>
        </div>
        <nav>
          <a className="nav-active" href="#dashboard">
            Dashboard
          </a>
          <a href="https://github.com/michelmartins75/devos-3" target="_blank" rel="noreferrer">
            Repositório
          </a>
          <a href="/docs/charter/devos-3.0-carta-de-fundacao.md" target="_blank" rel="noreferrer">
            Carta de fundação
          </a>
        </nav>
        <footer className="sidebar-foot">
          <small>Fase 1 · Leva 1</small>
          <small>Auth provisório via header</small>
        </footer>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <h1>Dashboard</h1>
            <p>Fundação multi-tenant — isolamento, auditoria e inferência nativos.</p>
          </div>
          <button type="button" onClick={() => void refresh()} disabled={loading}>
            {loading ? "Atualizando…" : "Atualizar"}
          </button>
        </header>

        <section className="panel">
          <h2>Contexto de tenant</h2>
          <p className="hint">
            Provisório até ADR-003. Enviado como <code>X-Tenant-ID</code> para a API.
          </p>
          <label className="field">
            <span>UUID do tenant</span>
            <input
              type="text"
              value={tenantId}
              onChange={(event) => setTenantId(event.target.value)}
              placeholder="00000000-0000-0000-0000-000000000000"
              spellCheck={false}
            />
          </label>
        </section>

        <section className="grid">
          <article className={`card ${status?.status === "ok" ? "ok" : "warn"}`}>
            <h3>API</h3>
            {error ? (
              <p className="error">{error}</p>
            ) : (
              <>
                <p className="metric">{status?.status ?? "—"}</p>
                <dl>
                  <div>
                    <dt>Ambiente</dt>
                    <dd>{status?.environment ?? "—"}</dd>
                  </div>
                  <div>
                    <dt>Versão</dt>
                    <dd>{status?.version ?? "—"}</dd>
                  </div>
                  <div>
                    <dt>Tenant reconhecido</dt>
                    <dd>{status?.tenant_id ?? "nenhum"}</dd>
                  </div>
                </dl>
              </>
            )}
          </article>

          <article className="card muted">
            <h3>Próximas capacidades</h3>
            <ul>
              <li>Work items e pipeline de 6 estágios (Leva 2)</li>
              <li>Roteador de inferência por tenant (F3)</li>
              <li>Camada cliente / captura de intenção (Fase 5)</li>
            </ul>
          </article>
        </section>
      </main>
    </div>
  );
}

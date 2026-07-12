const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8080";

export type HealthResponse = {
  status: string;
  environment: string;
};

export type StatusResponse = HealthResponse & {
  version: string;
  tenant_id: string | null;
};

function tenantHeaders(tenantId: string | null): HeadersInit {
  if (!tenantId) {
    return {};
  }
  return { "X-Tenant-ID": tenantId };
}

export async function fetchHealth(tenantId: string | null): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`, {
    headers: tenantHeaders(tenantId),
  });
  if (!response.ok) {
    throw new Error(`health check failed (${response.status})`);
  }
  return response.json() as Promise<HealthResponse>;
}

export async function fetchStatus(tenantId: string | null): Promise<StatusResponse> {
  const response = await fetch(`${API_BASE}/api/v1/status`, {
    headers: tenantHeaders(tenantId),
  });
  if (!response.ok) {
    throw new Error(`status check failed (${response.status})`);
  }
  return response.json() as Promise<StatusResponse>;
}

export { API_BASE };

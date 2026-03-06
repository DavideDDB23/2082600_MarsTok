/**
 * api/client.ts — Low-level typed HTTP helpers.
 *
 * All requests are relative to /api so the Vite dev-server proxy (or nginx
 * in production) can forward them to the FastAPI backend transparently.
 */

const BASE = "/api";

async function request<T>(
  method: string,
  path:   string,
  body?:  unknown,
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body !== undefined ? { "Content-Type": "application/json" } : {},
    body:    body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${method} ${path} → ${res.status}: ${text}`);
  }

  // 204 No Content
  if (res.status === 204) return undefined as unknown as T;

  return res.json() as Promise<T>;
}

export const get    = <T>(path: string)                     => request<T>("GET",    path);
export const post   = <T>(path: string, body: unknown)      => request<T>("POST",   path, body);
export const put    = <T>(path: string, body: unknown)      => request<T>("PUT",    path, body);
export const patch  = <T>(path: string, body?: unknown)     => request<T>("PATCH",  path, body);
export const del    = <T = void>(path: string)              => request<T>("DELETE", path);

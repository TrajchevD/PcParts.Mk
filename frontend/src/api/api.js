/**
 * Unified API client for PcPartsMk.
 *
 * All requests go through `apiFetch`. It:
 *  - Automatically injects the Authorization header from localStorage
 *  - Parses JSON responses
 *  - Throws a structured Error with the server's `detail` message on failure
 *  - Handles 401 responses by clearing the stale token
 */

export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// Keep the old `API` export for any direct-URL usage
export const API = API_BASE;

export async function apiFetch(url, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(API_BASE + url, {
    ...options,
    headers,
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    // Non-JSON body (e.g. 204 No Content) — that's fine
  }

  if (!res.ok) {
    // Auto-clear a stale/expired token on 401
    if (res.status === 401) {
      localStorage.removeItem("token");
    }
    const message = data?.detail || data?.message || `Request failed (${res.status})`;
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }

  return data;
}

/**
 * Unauthenticated GET helper — useful for public endpoints.
 * Kept for backward compatibility; prefer `apiFetch` for new code.
 */
export async function apiGet(path) {
  return apiFetch(path, { method: "GET", headers: { Authorization: undefined } });
}

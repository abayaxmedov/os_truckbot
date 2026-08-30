// Base API URL. In dev, Vite proxies /api and /media to the backend (same-origin).
// In production set VITE_API_BASE to the backend origin.
export const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) || "";

let authToken: string | null = null;

export function setToken(token: string | null) {
  authToken = token;
}
export function getToken(): string | null {
  return authToken;
}

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOpts {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
  form?: FormData;
}

export async function request<T>(path: string, opts: RequestOpts = {}): Promise<T> {
  const url = new URL(API_BASE + "/api/v1" + path, window.location.origin);
  if (opts.query) {
    for (const [k, v] of Object.entries(opts.query)) {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    }
  }

  const headers: Record<string, string> = {
    // Bypass the ngrok free-tier browser-warning interstitial on API/XHR calls.
    "ngrok-skip-browser-warning": "true",
  };
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

  let body: BodyInit | undefined;
  if (opts.form) {
    body = opts.form;
  } else if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }

  const res = await fetch(url.toString(), {
    method: opts.method || (body ? "POST" : "GET"),
    headers,
    body,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export function mediaUrl(path: string | null | undefined): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return API_BASE + path;
}

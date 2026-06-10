/**
 * Tiny typed fetch wrapper for the FastAPI backend.
 *
 * Reads NEXT_PUBLIC_API_BASE_URL (defaults to /api proxy in production where
 * Next.js and FastAPI share a domain via reverse-proxy; localhost:8000/api in dev).
 *
 * Phase 3+: this is the surface where auth headers will be injected.
 */

const RAW_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api';
// Strip trailing slash so path joins are predictable.
const API_BASE = RAW_BASE.replace(/\/$/, '');

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly url: string,
    message: string,
    public readonly body?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  signal?: AbortSignal;
  // Server-side calls in Next.js need cache control; client calls don't care.
  cache?: RequestCache;
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = new URL(`${API_BASE}${path.startsWith('/') ? path : `/${path}`}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

export async function apiRequest<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const url = buildUrl(path, opts.query);
  const init: RequestInit = {
    method: opts.method ?? 'GET',
    headers: opts.body ? {'Content-Type': 'application/json'} : undefined,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    signal: opts.signal,
    cache: opts.cache ?? 'no-store'
  };

  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (err) {
    throw new ApiError(0, url, `Network error: ${(err as Error).message}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const parsed = text ? safeParse(text) : undefined;

  if (!response.ok) {
    const message =
      (typeof parsed === 'object' && parsed && 'detail' in parsed
        ? String((parsed as {detail: unknown}).detail)
        : response.statusText) || 'Request failed';
    throw new ApiError(response.status, url, message, parsed);
  }

  return parsed as T;
}

function safeParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

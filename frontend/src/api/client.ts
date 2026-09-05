// Thin typed client over the existing FastAPI backend. No business logic
// lives here — it only calls the real API and shapes/reports errors; the
// UI never fabricates a response.

import type { ChatResponse, HealthResponse, WardrobeItem } from "../types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch (cause) {
    console.error(`Ornatus API request failed: ${path}`, cause);
    throw new ApiError("Could not reach Ornatus. Please check your connection and try again.");
  }

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body = await response.json();
      detail = body?.detail;
    } catch {
      // response wasn't JSON — fall through with no detail
    }
    console.error(`Ornatus API error ${response.status} on ${path}: ${detail ?? "no detail"}`);
    throw new ApiError("Something went wrong. Please try again.", response.status);
  }

  return response.json() as Promise<T>;
}

export function chat(message: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export function getWardrobe(): Promise<WardrobeItem[]> {
  return request<WardrobeItem[]>("/wardrobe");
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

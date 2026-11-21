// @vitest-environment node
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";

import { server } from "./server";

const BASE = "http://localhost/v1";

beforeAll(() => server.listen({ onUnhandledFrame: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("v1 mock API handlers", () => {
  it("POST /chat passes through to a real server; other endpoints stay mocked", async () => {
    // A tiny real HTTP server stands in for the FastAPI backend.
    let hits = 0;
    const real = createServer((_req, res) => {
      hits += 1;
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ reply: "from-real-server" }));
    });
    await new Promise<void>((ok) => real.listen(0, "127.0.0.1", ok));
    const { port } = real.address() as AddressInfo;
    const origin = `http://127.0.0.1:${port}`;
    try {
      const chat = await fetch(`${origin}/v1/chat`, { method: "POST" });
      expect(await chat.json()).toEqual({ reply: "from-real-server" });
      expect(hits).toBe(1);

      const mood = await fetch(`${origin}/v1/mood`, { method: "POST" });
      expect(mood.status).toBe(201);
      expect(hits).toBe(1); // mood was answered by the mock, not the server
    } finally {
      await new Promise((ok) => real.close(ok));
    }
  });

  it("POST /mood returns 201 with id + created_at", async () => {
    const res = await fetch(`${BASE}/mood`, { method: "POST" });
    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty("id");
    expect(body).toHaveProperty("created_at");
  });

  it("GET /mood/trends returns window + points array", async () => {
    const res = await fetch(`${BASE}/mood/trends`);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty("window");
    expect(Array.isArray(body.points)).toBe(true);
  });

  it("GET /memory returns items array", async () => {
    const res = await fetch(`${BASE}/memory`);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body.items)).toBe(true);
  });

  it("PATCH /memory returns the updated item", async () => {
    const res = await fetch(`${BASE}/memory`, { method: "PATCH" });
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty("item");
  });

  it("DELETE /memory returns 204", async () => {
    const res = await fetch(`${BASE}/memory`, { method: "DELETE" });
    expect(res.status).toBe(204);
  });

  it("GET /export returns a placeholder reference", async () => {
    const res = await fetch(`${BASE}/export`);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty("url");
  });

  it("DELETE /account returns 204", async () => {
    const res = await fetch(`${BASE}/account`, { method: "DELETE" });
    expect(res.status).toBe(204);
  });

  it("GET /crisis-resources returns placeholders with NO invented phone numbers", async () => {
    const res = await fetch(`${BASE}/crisis-resources`);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body.resources)).toBe(true);
    for (const r of body.resources) {
      // No fabricated phone numbers: phone must be null/empty in the mock.
      expect(r.phone === null || r.phone === "").toBe(true);
    }
  });
});
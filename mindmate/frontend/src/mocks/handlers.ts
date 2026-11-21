import { http, HttpResponse, passthrough } from "msw";

/*
  Mock API for the MindMate v1 endpoints (see design.md section 6).
  Placeholder data only. In particular, /v1/crisis-resources returns a clearly
  labelled PLACEHOLDER with NO invented phone numbers — real helplines are
  human-authored into the crisis_resources table later.

  /v1/chat is NOT mocked: it passes through to the real FastAPI backend.
  The other endpoints stay mocked until login (auth) exists, because the real
  backend returns 500 for them without a signed-in user.
*/

const BASE = "*/v1";

export const handlers = [
  // Chat: served by the real backend.
  http.post(`${BASE}/chat`, () => passthrough()),

  // Mood: record a mood entry.
  http.post(`${BASE}/mood`, async () => {
    return HttpResponse.json(
      { id: "00000000-0000-0000-0000-000000000000", created_at: "1970-01-01T00:00:00Z" },
      { status: 201 },
    );
  }),

  // Mood trends.
  http.get(`${BASE}/mood/trends`, () => {
    return HttpResponse.json({ window: "7d", points: [] });
  }),

  // Memory: list.
  http.get(`${BASE}/memory`, () => {
    return HttpResponse.json({ items: [] });
  }),

  // Memory: update one item.
  http.patch(`${BASE}/memory`, async () => {
    return HttpResponse.json({
      item: { id: "00000000-0000-0000-0000-000000000000", content: "PLACEHOLDER" },
    });
  }),

  // Memory: delete.
  http.delete(`${BASE}/memory`, () => {
    return new HttpResponse(null, { status: 204 });
  }),

  // Export: placeholder download reference.
  http.get(`${BASE}/export`, () => {
    return HttpResponse.json({ url: "PLACEHOLDER", format: "json" });
  }),

  // Account deletion.
  http.delete(`${BASE}/account`, () => {
    return new HttpResponse(null, { status: 204 });
  }),

  // Crisis resources: PLACEHOLDER only, no invented numbers.
  http.get(`${BASE}/crisis-resources`, () => {
    return HttpResponse.json({
      resources: [
        {
          id: "PLACEHOLDER",
          country_code: null,
          language: null,
          name: "PLACEHOLDER — human-authored helpline",
          phone: null,
          url: null,
          notes: "Populated from crisis_resources table; no numbers invented.",
          is_active: false,
        },
      ],
    });
  }),
];
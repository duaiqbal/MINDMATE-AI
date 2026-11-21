import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";

import AppShell from "./AppShell";
import i18n from "./i18n";
import { server } from "./mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

function renderApp() {
  const qc = new QueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={["/"]}>
        <AppShell />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("app screens", () => {
  it("shows consent gate first and reveals nav after agreeing", async () => {
    await i18n.changeLanguage("en");
    renderApp();
    // consent visible, nav not yet
    expect(screen.getByText("Before we begin")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "I understand and agree" }));
    // after consent, primary nav appears
    await waitFor(() =>
      expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument(),
    );
  });

  it("logs a mood via the mock API", async () => {
    await i18n.changeLanguage("en");
    renderApp();
    fireEvent.click(screen.getByRole("button", { name: "I understand and agree" }));
    fireEvent.click(await screen.findByText("Mood"));
    const five = await screen.findByRole("button", { name: "5" });
    fireEvent.click(five);
    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent("Mood logged"),
    );
  });
});
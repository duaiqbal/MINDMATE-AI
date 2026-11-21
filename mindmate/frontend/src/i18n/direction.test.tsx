import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import AppShell from "../AppShell";
import i18n from "./index";

async function renderConsented() {
  const qc = new QueryClient();
  render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <AppShell />
      </MemoryRouter>
    </QueryClientProvider>,
  );
  fireEvent.click(screen.getByRole("button", { name: /agree|raazi/i }));
  await waitFor(() => screen.getByRole("navigation", { name: "Primary" }));
}

describe("language + direction (en + roman_ur, both LTR)", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("en");
  });

  it("is ltr for English", async () => {
    await renderConsented();
    expect(document.documentElement.getAttribute("dir")).toBe("ltr");
    expect(document.documentElement.getAttribute("lang")).toBe("en");
  });

  it("switches to Roman Urdu and stays ltr", async () => {
    await renderConsented();
    fireEvent.click(screen.getByRole("button", { name: "Roman Urdu" }));
    await Promise.resolve();
    expect(document.documentElement.getAttribute("dir")).toBe("ltr");
    expect(document.documentElement.getAttribute("lang")).toBe("roman_ur");
  });

  it("offers exactly two languages", async () => {
    await renderConsented();
    expect(screen.getByRole("button", { name: "English" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Roman Urdu" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "اردو" })).not.toBeInTheDocument();
  });
});
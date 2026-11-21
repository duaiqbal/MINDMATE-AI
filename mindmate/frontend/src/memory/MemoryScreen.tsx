import { useTranslation } from "react-i18next";

import { useDeleteMemory, useMemory } from "../api/hooks";

export function MemoryScreen() {
  const { t } = useTranslation();
  const { data } = useMemory();
  const del = useDeleteMemory();
  const items = data?.items ?? [];

  return (
    <section className="mx-auto max-w-2xl">
      <h2 className="mb-4 text-xl font-semibold text-ink">{t("memory.title")}</h2>
      {items.length === 0 ? (
        <p className="text-ink-muted">{t("memory.empty")}</p>
      ) : (
        <ul className="space-y-2">
          {items.map((m) => (
            <li
              key={m.id}
              className="flex items-center justify-between rounded-lg bg-surface p-3"
            >
              <span className="text-ink">{m.content}</span>
              <button
                type="button"
                className="rounded-md bg-accent px-3 py-1 text-surface"
                onClick={() => del.mutate(m.id)}
              >
                {t("memory.delete")}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
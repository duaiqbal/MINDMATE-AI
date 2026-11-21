import { useTranslation } from "react-i18next";

import { LanguageSwitcher } from "../LanguageSwitcher";
import { api } from "../api/client";

export function SettingsScreen() {
  const { t } = useTranslation();

  return (
    <section className="mx-auto max-w-xl space-y-6">
      <h2 className="text-xl font-semibold text-ink">{t("settings.title")}</h2>
      <div>
        <h3 className="mb-2 text-ink-muted">{t("settings.language")}</h3>
        <LanguageSwitcher />
      </div>
      <div className="flex gap-3">
        <button
          type="button"
          className="rounded-md bg-primary px-4 py-2 text-surface"
          onClick={() => void api.get("/v1/export")}
        >
          {t("settings.export")}
        </button>
        <button
          type="button"
          className="rounded-md bg-accent px-4 py-2 text-surface"
          onClick={() => void api.del("/v1/account")}
        >
          {t("settings.deleteAccount")}
        </button>
      </div>
    </section>
  );
}
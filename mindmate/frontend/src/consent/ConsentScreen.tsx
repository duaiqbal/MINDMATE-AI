import { useState } from "react";
import { useTranslation } from "react-i18next";

export function ConsentScreen({ onConsent }: { onConsent: () => void }) {
  const { t } = useTranslation();
  const [error, setError] = useState(false);

  return (
    <section className="mx-auto max-w-xl rounded-xl bg-surface p-6 shadow-sm">
      <h2 className="mb-3 text-xl font-semibold text-ink">{t("consent.title")}</h2>
      <p className="mb-6 text-ink-muted">{t("consent.body")}</p>
      {error && (
        <p role="alert" className="mb-3 text-accent">
          {t("consent.required")}
        </p>
      )}
      <button
        type="button"
        className="rounded-md bg-primary px-4 py-2 text-surface"
        onClick={() => {
          setError(false);
          onConsent();
        }}
      >
        {t("consent.agree")}
      </button>
    </section>
  );
}
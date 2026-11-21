import { useTranslation } from "react-i18next";

import { useLogMood } from "../api/hooks";

const SCORES = [1, 2, 3, 4, 5];

export function MoodScreen() {
  const { t } = useTranslation();
  const log = useLogMood();

  return (
    <section className="mx-auto max-w-md text-center">
      <h2 className="mb-4 text-xl font-semibold text-ink">{t("mood.title")}</h2>
      <p className="mb-4 text-ink-muted">{t("mood.prompt")}</p>
      <div role="group" aria-label={t("mood.prompt")} className="flex justify-center gap-2">
        {SCORES.map((s) => (
          <button
            key={s}
            type="button"
            className="h-12 w-12 rounded-full bg-primary-soft text-ink"
            onClick={() => log.mutate(s)}
          >
            {s}
          </button>
        ))}
      </div>
      {log.isSuccess && (
        <p role="status" className="mt-4 text-primary">
          {t("mood.logged")}
        </p>
      )}
    </section>
  );
}
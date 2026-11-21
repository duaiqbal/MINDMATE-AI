import { useTranslation } from "react-i18next";

import { SUPPORTED_LANGUAGES, type AppLanguage } from "./i18n/languages";

const LABELS: Record<AppLanguage, string> = {
  en: "English",
  roman_ur: "Roman Urdu",
};

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  return (
    <div role="group" aria-label="Language" className="flex gap-2">
      {SUPPORTED_LANGUAGES.map((lang) => (
        <button
          key={lang}
          type="button"
          aria-pressed={i18n.language === lang}
          onClick={() => void i18n.changeLanguage(lang)}
          className="rounded-md bg-primary px-3 py-1 text-surface"
        >
          {LABELS[lang]}
        </button>
      ))}
    </div>
  );
}
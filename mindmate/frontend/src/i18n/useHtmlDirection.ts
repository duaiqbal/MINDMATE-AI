import { useEffect } from "react";
import { useTranslation } from "react-i18next";

import { directionFor } from "./languages";

/** Syncs <html lang> and <html dir> with the active i18n language. */
export function useHtmlDirection(): void {
  const { i18n } = useTranslation();
  useEffect(() => {
    const lang = i18n.language;
    document.documentElement.setAttribute("lang", lang);
    document.documentElement.setAttribute("dir", directionFor(lang));
  }, [i18n.language]);
}
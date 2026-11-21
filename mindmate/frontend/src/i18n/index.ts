import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import roman_ur from "./locales/roman_ur.json";
import { SUPPORTED_LANGUAGES } from "./languages";

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    roman_ur: { translation: roman_ur },
  },
  lng: "en",
  fallbackLng: "en",
  supportedLngs: SUPPORTED_LANGUAGES as unknown as string[],
  interpolation: { escapeValue: false },
});

export default i18n;
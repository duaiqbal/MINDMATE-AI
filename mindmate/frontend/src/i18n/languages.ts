export const SUPPORTED_LANGUAGES = ["en", "roman_ur"] as const;
export type AppLanguage = (typeof SUPPORTED_LANGUAGES)[number];

// Current scope supports English + Roman Urdu; both use Latin script (LTR).
// Urdu script was removed from scope. The helper stays for possible future use.
export const RTL_LANGUAGES: readonly string[] = [];

export function directionFor(lang: string): "rtl" | "ltr" {
  return RTL_LANGUAGES.includes(lang) ? "rtl" : "ltr";
}
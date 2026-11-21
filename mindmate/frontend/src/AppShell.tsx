import { useState } from "react";
import { useTranslation } from "react-i18next";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";

import { ConsentScreen } from "./consent/ConsentScreen";
import { ChatScreen } from "./chat/ChatScreen";
import { MoodScreen } from "./mood/MoodScreen";
import { DashboardScreen } from "./dashboard/DashboardScreen";
import { MemoryScreen } from "./memory/MemoryScreen";
import { SettingsScreen } from "./settings/SettingsScreen";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useHtmlDirection } from "./i18n/useHtmlDirection";

const NAV = [
  { to: "/chat", key: "nav.chat" },
  { to: "/mood", key: "nav.mood" },
  { to: "/dashboard", key: "nav.dashboard" },
  { to: "/memory", key: "nav.memory" },
  { to: "/settings", key: "nav.settings" },
] as const;

export default function AppShell() {
  useHtmlDirection();
  const { t } = useTranslation();
  const [consented, setConsented] = useState(false);

  if (!consented) {
    return (
      <main className="min-h-screen bg-bg p-6">
        <ConsentScreen onConsent={() => setConsented(true)} />
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-bg">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-sand bg-surface px-6 py-3">
        <span className="text-lg font-semibold text-primary">{t("app.title")}</span>
        <nav className="flex gap-3" aria-label="Primary">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                isActive ? "font-semibold text-primary" : "text-ink-muted"
              }
            >
              {t(n.key)}
            </NavLink>
          ))}
        </nav>
        <LanguageSwitcher />
      </header>
      <main className="p-6">
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatScreen />} />
          <Route path="/mood" element={<MoodScreen />} />
          <Route path="/dashboard" element={<DashboardScreen />} />
          <Route path="/memory" element={<MemoryScreen />} />
          <Route path="/settings" element={<SettingsScreen />} />
        </Routes>
      </main>
    </div>
  );
}
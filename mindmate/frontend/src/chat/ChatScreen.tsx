import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useSendChat } from "../api/hooks";

export function ChatScreen() {
  const { t } = useTranslation();
  const [text, setText] = useState("");
  const [log, setLog] = useState<{ role: string; content: string }[]>([]);
  const send = useSendChat();

  const onSend = () => {
    if (!text.trim()) return;
    const message = text;
    setLog((l) => [...l, { role: "user", content: message }]);
    setText("");
    send.mutate(message, {
      onSuccess: (reply) =>
        setLog((l) => [...l, { role: "assistant", content: reply.reply }]),
      onError: () =>
        setLog((l) => [...l, { role: "error", content: t("chat.error") }]),
    });
  };

  return (
    <section className="mx-auto max-w-2xl">
      <h2 className="mb-2 text-xl font-semibold text-ink">{t("chat.title")}</h2>
      <p className="mb-4 text-sm text-ink-muted">{t("chat.disclaimer")}</p>
      <ul className="mb-4 space-y-2" aria-live="polite">
        {log.map((m, i) => (
          <li
            key={i}
            className={
              m.role === "user"
                ? "rounded-lg bg-primary-soft p-2 text-ink"
                : m.role === "error"
                  ? "rounded-lg bg-surface p-2 text-accent"
                  : "rounded-lg bg-surface p-2 text-ink"
            }
          >
            {m.content}
          </li>
        ))}
      </ul>
      <div className="flex gap-2">
        <label className="sr-only" htmlFor="chat-input">
          {t("chat.placeholder")}
        </label>
        <input
          id="chat-input"
          className="flex-1 rounded-md border border-sand bg-surface p-2 text-ink"
          placeholder={t("chat.placeholder")}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSend()}
        />
        <button
          type="button"
          className="rounded-md bg-primary px-4 py-2 text-surface"
          onClick={onSend}
        >
          {t("chat.send")}
        </button>
      </div>
    </section>
  );
}
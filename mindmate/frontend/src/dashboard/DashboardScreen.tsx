import { useTranslation } from "react-i18next";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useMoodTrends } from "../api/hooks";

export function DashboardScreen() {
  const { t } = useTranslation();
  const { data, isLoading } = useMoodTrends();
  const points = data?.points ?? [];

  return (
    <section className="mx-auto max-w-2xl">
      <h2 className="mb-4 text-xl font-semibold text-ink">{t("dashboard.title")}</h2>
      <h3 className="mb-2 text-ink-muted">{t("dashboard.trend")}</h3>
      {isLoading ? null : points.length === 0 ? (
        <p className="text-ink-muted">{t("dashboard.empty")}</p>
      ) : (
        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={points}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis domain={[1, 5]} />
              <Tooltip />
              {/* data-blue is used for the chart series (AA for graphics) */}
              <Line type="monotone" dataKey="average_mood" stroke="#5F7F96" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
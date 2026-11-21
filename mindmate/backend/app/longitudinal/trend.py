"""Simple mood trend: per-day average over a window. No fancy stats."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime


def compute_trend(moods: list[dict], window_days: int) -> list[dict]:
    """Return per-day average mood + count, sorted by day ascending.

    ``moods`` is a list of rows with 'mood' (int) and 'created_at' (datetime).
    """
    buckets: dict[str, list[int]] = defaultdict(list)
    for m in moods:
        created: datetime = m["created_at"]
        day = created.date().isoformat()
        buckets[day].append(int(m["mood"]))

    points = []
    for day in sorted(buckets):
        vals = buckets[day]
        points.append(
            {
                "day": day,
                "average_mood": round(sum(vals) / len(vals), 2),
                "count": len(vals),
            }
        )
    return points
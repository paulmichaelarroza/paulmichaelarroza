from __future__ import annotations

import datetime as dt
import sqlite3
from dataclasses import dataclass


@dataclass
class DashboardSummary:
    total_kpis: int
    avg_achievement_pct: float
    below_threshold: int
    ytd_achievement_pct: float
    projects_at_risk: int


def forecast_next(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    x = list(range(len(values)))
    x_mean = sum(x) / len(x)
    y_mean = sum(values) / len(values)
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    if denominator == 0:
        return values[-1]
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return round(intercept + slope * len(values), 2)


def calculate_dashboard(conn: sqlite3.Connection) -> DashboardSummary:
    rows = conn.execute(
        """SELECT k.id, e.target_value, e.actual_value, k.threshold_pct, e.period
        FROM kpis k
        LEFT JOIN kpi_entries e ON e.kpi_id = k.id"""
    ).fetchall()

    valid = [r for r in rows if r["target_value"] and r["target_value"] != 0]
    total_kpis = conn.execute("SELECT COUNT(*) FROM kpis").fetchone()[0]
    if not valid:
        avg = 0.0
        below = 0
        ytd = 0.0
    else:
        achievements = [(r["actual_value"] / r["target_value"]) * 100 for r in valid]
        avg = round(sum(achievements) / len(achievements), 2)
        below = sum(1 for r in valid if (r["actual_value"] / r["target_value"]) * 100 < r["threshold_pct"])
        ytd_rows = [r for r in valid if r["period"].startswith(str(dt.datetime.utcnow().year))]
        ytd = (
            round(sum((r["actual_value"] / r["target_value"]) * 100 for r in ytd_rows) / len(ytd_rows), 2)
            if ytd_rows
            else 0.0
        )

    at_risk = conn.execute("SELECT COUNT(*) FROM projects WHERE status IN ('at_risk','delayed')").fetchone()[0]
    return DashboardSummary(
        total_kpis=total_kpis,
        avg_achievement_pct=avg,
        below_threshold=below,
        ytd_achievement_pct=ytd,
        projects_at_risk=at_risk,
    )

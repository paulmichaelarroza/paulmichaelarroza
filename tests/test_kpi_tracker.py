import sqlite3

from kpi_tracker.analytics import calculate_dashboard, forecast_next


def test_forecast_next_linear_growth():
    assert forecast_next([10, 20, 30]) == 40.0


def test_calculate_dashboard_summary():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE kpis (id INTEGER PRIMARY KEY, threshold_pct REAL);
        CREATE TABLE kpi_entries (id INTEGER PRIMARY KEY, kpi_id INTEGER, period TEXT, target_value REAL, actual_value REAL);
        CREATE TABLE projects (id INTEGER PRIMARY KEY, status TEXT);
        INSERT INTO kpis(id, threshold_pct) VALUES (1, 90), (2, 90);
        INSERT INTO kpi_entries(kpi_id, period, target_value, actual_value) VALUES
            (1, '2026-01', 100, 80),
            (2, '2026-01', 100, 100);
        INSERT INTO projects(status) VALUES ('at_risk'), ('completed');
        """
    )

    summary = calculate_dashboard(conn)
    assert summary.total_kpis == 2
    assert summary.below_threshold == 1
    assert summary.projects_at_risk == 1

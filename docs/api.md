# KPI Tracker API Documentation

Base URL: `/api`

## Authentication
- `POST /auth/login` - Email/password login.
- `POST /auth/oauth` - Google/Microsoft OAuth token exchange.

## Core APIs
- `GET /kpis` - List KPIs by role scope.
- `POST /kpi/update` - Submit KPI actual and auto-compute variance/achievement/status.
- `POST /kpi/upload` - Bulk upload KPI actuals via CSV/XLSX.
- `GET /dashboard` - Executive summary, top/missed KPIs, site comparison, forecast alerts.
- `GET /sites` - Site listing filtered by RBAC.
- `GET /projects` - Project monitoring list.
- `POST /projects` - Create project (Super Admin/Site Manager).
- `GET /health` - Service health check.

## KPI Logic
- `Achievement % = (Actual / Target) * 100`
- Status:
  - `HIT` if `Actual >= Target`
  - `AT_RISK` if `Achievement >= 90` but `< 100`
  - `MISS` otherwise

## Time Tracking Dimensions
The model stores KPI monthly values and supports rollups for:
- Monthly
- Quarterly (aggregate 3 months)
- YTD
- Annual

## Integrations
This starter provides REST APIs to connect WMS, ERP, CRM, and Power BI. Add API keys/service accounts per environment.

## OpenAPI
Run backend and open: `http://localhost:8000/docs`

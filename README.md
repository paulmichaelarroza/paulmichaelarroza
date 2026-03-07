# Enterprise AI-Powered KPI Tracker

Production-ready KPI monitoring platform for multi-site enterprise operations.

## Covered Enterprise Requirements
- Multi-site KPI hierarchy: Company → Site → Department → KRA → KPI.
- Sites pre-seeded: Glacier South, Glacier Pulilan, Glacier Manila, Glacier Davao.
- RBAC roles: Super Admin, Executive, Site Manager, Encoder.
- Auth methods: Email/password plus OAuth2 stubs for Google/Microsoft.
- KPI computation: target/actual, variance, achievement %, HIT/MISS/AT_RISK.
- Period tracking: monthly data model with quarterly/YTD/annual rollup support.
- Executive dashboards: scorecards, site comparison, top/missed KPIs, forecast alerts.
- Project monitoring module with ownership, progress, status.
- AI forecasting module using time-series regression for risk alerts.
- Data encoding: manual entry + CSV/Excel bulk upload.
- Alert foundation: notification table and service hooks for Email/Teams/Slack.
- REST APIs for integration (WMS/ERP/CRM/Power BI).
- Dockerized deployment with PostgreSQL.

## Architecture
- **Frontend:** React + Vite + Recharts (`frontend/`)
- **Backend:** FastAPI + SQLAlchemy (`backend/`)
- **DB:** PostgreSQL (`docker-compose`)
- **ML Forecasting:** scikit-learn regression (`backend/app/ml/forecasting.py`)

## Quick Start (Docker)
```bash
docker compose up --build -d
```

Seed data:
```bash
docker compose exec backend python -m app.seed.seed_data
```

Access:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Local Development
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Demo Users
- Super Admin: `admin@kpi.local / admin123`
- Executive: `exec@kpi.local / exec123`
- Site Managers/Encoders are seeded per site (`manager{siteId}@kpi.local`, `encoder{siteId}@kpi.local`).

## API Summary
See `docs/api.md` for endpoint details.

## Database Schema
See `docs/database_schema.sql` for DDL.

## Sample Dataset
See `data/sample_kpi_actuals.csv` for bulk KPI import template.

# KPI Tracker Web App (with OCR utility retained)

This repository now includes a **complete KPI Tracker application** plus the original OCR utility.

## KPI Tracker capabilities

- KPI setup per **department** and **KRA**.
- Target vs Actual encoding by regular users (raw data input).
- **Monthly and YTD** tracking.
- **Forecasting** of next KPI value (linear trend).
- Project monitoring (status, progress, budget/spent).
- Executive dashboard visibility for managers/admin only.
- Role-based users (`user`, `manager`, `admin`).
- Local login + OAuth integration readiness for **Google** and **Microsoft 365**.
- Email notification support for KPI threshold breaches (SMTP configurable).
- API-first design with import endpoint for CSV raw file upload.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn kpi_tracker.app:app --host 0.0.0.0 --port 8000
```

Open:

- `http://localhost:8000/` login page
- `http://localhost:8000/app` dashboard
- `http://localhost:8000/docs` API docs

Default admin account:

- Email: `admin@kpi.local`
- Password: `ChangeMe123!`

## SMTP configuration (for automated alerts)

Set environment variables:

```bash
export SMTP_HOST="smtp.your-provider.com"
export SMTP_PORT="587"
export SMTP_USER="your-user"
export SMTP_PASSWORD="your-password"
export SMTP_SENDER="alerts@yourcompany.com"
```

Then run alerts via manager endpoint:

- `POST /api/v1/alerts/run`

## OAuth integration readiness

- `GET /api/v1/auth/oauth/providers`

This returns Google/Microsoft OAuth endpoints for integration setup. You can wire your enterprise SSO (MS365/Azure AD) or personal Gmail OAuth app settings.

## Important API endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/departments`
- `POST /api/v1/kpis`
- `POST /api/v1/kpi-entries`
- `POST /api/v1/import/raw` (CSV upload)
- `POST /api/v1/projects`
- `GET /api/v1/dashboard`

## Existing OCR Utility (kept)

You can still use the original scan-to-text app:

```bash
python scan_to_text_app.py scan-image --input sample.png --output output.txt
python scan_to_text_app.py read-section --input output.txt --start "Invoice Number:" --end "Footer"
```

## Tests

```bash
pytest -q
```

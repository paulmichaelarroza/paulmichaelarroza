from collections import defaultdict
from datetime import datetime
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.ml.forecasting import forecast_next_value
from app.models.entities import (
    Department,
    KPI,
    KPIActual,
    KPITarget,
    Project,
    Site,
    User,
)
from app.schemas.common import (
    DashboardResponse,
    KPIActualCreate,
    KPIActualResponse,
    LoginRequest,
    OAuthLoginRequest,
    ProjectCreate,
    ProjectResponse,
    Token,
)
from app.services.kpi import calculate_kpi_metrics

router = APIRouter()


@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    return Token(access_token=create_access_token(user.email))


@router.post("/auth/oauth", response_model=Token)
def oauth_login(payload: OAuthLoginRequest, db: Session = Depends(get_db)):
    # Demo flow: token is accepted as provider subject in this starter template.
    user = (
        db.query(User)
        .filter(User.oauth_provider == payload.provider, User.oauth_subject == payload.token)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="OAuth user not found. Provision user first.")
    return Token(access_token=create_access_token(user.email))


@router.get("/sites")
def list_sites(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role.name in {"SUPER_ADMIN", "EXECUTIVE"}:
        return db.query(Site).all()
    if user.site_id:
        return db.query(Site).filter(Site.id == user.site_id).all()
    return []


@router.get("/kpis")
def list_kpis(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(KPI)
    if user.role.name not in {"SUPER_ADMIN", "EXECUTIVE"} and user.site_id:
        query = query.filter(KPI.site_id == user.site_id)
    if user.role.name == "ENCODER" and user.department_id:
        query = query.filter(KPI.department_id == user.department_id)
    return query.all()


@router.post("/kpi/update", response_model=KPIActualResponse)
def update_kpi(
    payload: KPIActualCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "SITE_MANAGER", "ENCODER")),
):
    target = (
        db.query(KPITarget)
        .filter(
            KPITarget.kpi_id == payload.kpi_id,
            KPITarget.year == payload.year,
            KPITarget.month == payload.month,
        )
        .first()
    )
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    variance, achievement, status = calculate_kpi_metrics(target.target_value, payload.actual_value)
    actual = KPIActual(
        kpi_id=payload.kpi_id,
        year=payload.year,
        month=payload.month,
        actual_value=payload.actual_value,
        variance=variance,
        achievement_percentage=achievement,
        status=status,
        created_by=user.id,
    )
    db.add(actual)
    db.commit()

    return KPIActualResponse(
        kpi_id=payload.kpi_id,
        target_value=target.target_value,
        actual_value=payload.actual_value,
        variance=variance,
        achievement_percentage=achievement,
        status=status,
    )


@router.post("/kpi/upload")
def upload_kpi_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "SITE_MANAGER", "ENCODER")),
):
    content = file.file.read()
    if file.filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(content))
    else:
        df = pd.read_excel(BytesIO(content))

    created = 0
    for row in df.to_dict(orient="records"):
        payload = KPIActualCreate(**row)
        target = (
            db.query(KPITarget)
            .filter(
                KPITarget.kpi_id == payload.kpi_id,
                KPITarget.year == payload.year,
                KPITarget.month == payload.month,
            )
            .first()
        )
        if not target:
            continue
        variance, achievement, status = calculate_kpi_metrics(target.target_value, payload.actual_value)
        db.add(
            KPIActual(
                kpi_id=payload.kpi_id,
                year=payload.year,
                month=payload.month,
                actual_value=payload.actual_value,
                variance=variance,
                achievement_percentage=achievement,
                status=status,
                created_by=user.id,
            )
        )
        created += 1

    db.commit()
    return {"created": created}


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(KPIActual, KPI, KPITarget).join(KPI, KPIActual.kpi_id == KPI.id).join(
        KPITarget,
        (KPITarget.kpi_id == KPIActual.kpi_id)
        & (KPITarget.year == KPIActual.year)
        & (KPITarget.month == KPIActual.month),
    )
    if user.role.name not in {"SUPER_ADMIN", "EXECUTIVE"} and user.site_id:
        query = query.filter(KPI.site_id == user.site_id)

    records = query.all()
    if not records:
        return DashboardResponse(
            company_score=0,
            site_comparison={},
            missed_kpis=0,
            top_kpis=[],
            forecast_alerts=[],
        )

    achievement_values = [r[0].achievement_percentage for r in records]
    site_scores = defaultdict(list)
    for actual, kpi, _ in records:
        site_scores[kpi.site_id].append(actual.achievement_percentage)
    site_comparison = {
        str(site_id): round(sum(vals) / len(vals), 2) for site_id, vals in site_scores.items()
    }

    grouped_values = defaultdict(list)
    for actual, _, _ in records:
        ym = actual.year * 100 + actual.month
        grouped_values[actual.kpi_id].append((ym, actual.actual_value))

    forecast_alerts = []
    for kpi_id, points in grouped_values.items():
        points = sorted(points)
        months = list(range(1, len(points) + 1))
        vals = [v for _, v in points]
        prediction = forecast_next_value(months, vals)
        latest_target = db.query(KPITarget).filter(KPITarget.kpi_id == kpi_id).order_by(KPITarget.year.desc(), KPITarget.month.desc()).first()
        if latest_target and prediction < latest_target.target_value:
            forecast_alerts.append({"kpi_id": kpi_id, "forecast": prediction, "target": latest_target.target_value})

    top_kpis = sorted(
        [{"kpi_id": a.kpi_id, "achievement": a.achievement_percentage} for a, _, _ in records],
        key=lambda x: x["achievement"],
        reverse=True,
    )[:5]

    return DashboardResponse(
        company_score=round(sum(achievement_values) / len(achievement_values), 2),
        site_comparison=site_comparison,
        missed_kpis=sum(1 for a, _, _ in records if a.status == "MISS"),
        top_kpis=top_kpis,
        forecast_alerts=forecast_alerts,
    )


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Project)
    if user.role.name not in {"SUPER_ADMIN", "EXECUTIVE"} and user.site_id:
        query = query.filter(Project.site_id == user.site_id)
    return query.all()


@router.post("/projects", response_model=ProjectResponse)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("SUPER_ADMIN", "SITE_MANAGER")),
):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/health")
def healthcheck():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

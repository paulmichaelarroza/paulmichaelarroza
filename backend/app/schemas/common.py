from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OAuthLoginRequest(BaseModel):
    provider: Literal["google", "microsoft"]
    token: str


class KPIActualCreate(BaseModel):
    kpi_id: int
    year: int
    month: int
    actual_value: float


class KPIActualResponse(BaseModel):
    kpi_id: int
    target_value: float
    actual_value: float
    variance: float
    achievement_percentage: float
    status: str


class DashboardResponse(BaseModel):
    company_score: float
    site_comparison: dict
    missed_kpis: int
    top_kpis: list[dict]
    forecast_alerts: list[dict]


class ProjectCreate(BaseModel):
    project_name: str
    owner_id: int
    department_id: int
    site_id: int
    start_date: date
    end_date: date
    progress_percentage: float = 0
    status: str = "Not Started"


class ProjectResponse(ProjectCreate):
    id: int

    class Config:
        from_attributes = True

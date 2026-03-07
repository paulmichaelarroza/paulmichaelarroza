from datetime import date

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import Department, KPI, KPIActual, KPITarget, KRA, Project, Role, Site, User
from app.services.kpi import calculate_kpi_metrics


SITES = ["Glacier South", "Glacier Pulilan", "Glacier Manila", "Glacier Davao"]
ROLES = ["SUPER_ADMIN", "EXECUTIVE", "SITE_MANAGER", "ENCODER"]


def seed(db: Session):
    if db.query(Role).count() > 0:
        return

    roles = {name: Role(name=name) for name in ROLES}
    db.add_all(roles.values())
    db.flush()

    sites = [Site(name=name) for name in SITES]
    db.add_all(sites)
    db.flush()

    departments = []
    for site in sites:
        for dep_name in ["Operations", "Logistics", "Finance"]:
            departments.append(Department(name=dep_name, site_id=site.id))
    db.add_all(departments)
    db.flush()

    users = [
        User(email="admin@kpi.local", full_name="Super Admin", hashed_password=hash_password("admin123"), role_id=roles["SUPER_ADMIN"].id),
        User(email="exec@kpi.local", full_name="Executive", hashed_password=hash_password("exec123"), role_id=roles["EXECUTIVE"].id),
    ]

    for site in sites:
        dep = next(d for d in departments if d.site_id == site.id and d.name == "Operations")
        users.append(User(email=f"manager{site.id}@kpi.local", full_name=f"{site.name} Manager", hashed_password=hash_password("manager123"), role_id=roles["SITE_MANAGER"].id, site_id=site.id, department_id=dep.id))
        users.append(User(email=f"encoder{site.id}@kpi.local", full_name=f"{site.name} Encoder", hashed_password=hash_password("encoder123"), role_id=roles["ENCODER"].id, site_id=site.id, department_id=dep.id))

    db.add_all(users)
    db.flush()

    operations_deps = [d for d in departments if d.name == "Operations"]
    kras = [KRA(name="Warehouse Efficiency", department_id=d.id) for d in operations_deps]
    db.add_all(kras)
    db.flush()

    kpi_names = ["Inventory Accuracy", "Order Picking Accuracy", "On-Time Dispatch", "Warehouse Utilization"]
    kpis = []
    for i, dep in enumerate(operations_deps):
        owner = next(u for u in users if u.site_id == dep.site_id and "Encoder" in u.full_name)
        kra = next(k for k in kras if k.department_id == dep.id)
        for name in kpi_names:
            kpis.append(KPI(name=name, unit_of_measure="%", owner_id=owner.id, site_id=dep.site_id, department_id=dep.id, kra_id=kra.id))
    db.add_all(kpis)
    db.flush()

    targets = []
    actuals = []
    for kpi in kpis:
        for month in [1, 2, 3, 4]:
            target_val = 95.0
            targets.append(KPITarget(kpi_id=kpi.id, period="monthly", year=2026, month=month, target_value=target_val))
            actual = 93 + ((kpi.id + month) % 6)
            variance, ach, status = calculate_kpi_metrics(target_val, actual)
            actuals.append(KPIActual(kpi_id=kpi.id, year=2026, month=month, actual_value=actual, variance=variance, achievement_percentage=ach, status=status, created_by=kpi.owner_id))

    db.add_all(targets)
    db.add_all(actuals)

    projects = [
        Project(project_name="Cold Chain Upgrade", owner_id=users[0].id, department_id=operations_deps[0].id, site_id=operations_deps[0].site_id, start_date=date(2026, 1, 1), end_date=date(2026, 9, 30), progress_percentage=56, status="In Progress"),
        Project(project_name="Dispatch Automation", owner_id=users[1].id, department_id=operations_deps[1].id, site_id=operations_deps[1].site_id, start_date=date(2026, 2, 15), end_date=date(2026, 11, 30), progress_percentage=34, status="Delayed"),
    ]
    db.add_all(projects)

    db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
        print("Seed complete")
    finally:
        db.close()

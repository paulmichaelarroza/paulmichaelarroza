def calculate_kpi_metrics(target: float, actual: float) -> tuple[float, float, str]:
    variance = round(actual - target, 2)
    achievement = round((actual / target) * 100, 2) if target else 0
    if actual >= target:
        status = "HIT"
    elif achievement >= 90:
        status = "AT_RISK"
    else:
        status = "MISS"
    return variance, achievement, status

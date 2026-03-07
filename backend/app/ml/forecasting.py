import numpy as np
from sklearn.linear_model import LinearRegression


def forecast_next_value(months: list[int], values: list[float]) -> float:
    if len(months) < 2 or len(values) < 2:
        return values[-1] if values else 0

    x = np.array(months).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression()
    model.fit(x, y)
    next_month = max(months) + 1
    prediction = model.predict(np.array([[next_month]]))[0]
    return float(round(prediction, 2))

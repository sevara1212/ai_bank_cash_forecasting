import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.data_loader import load_data
from backend.forecasting import compute_predictions

app = FastAPI(title="AI Bank Cash Forecast API", version="1.0.0")

frontend_origins = os.getenv("FRONTEND_ORIGINS", "*")
allowed_origins = ["*"] if frontend_origins.strip() == "*" else [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/forecast")
def forecast(forecast_days: int = 3) -> dict:
    if forecast_days < 1 or forecast_days > 14:
        raise HTTPException(status_code=400, detail="forecast_days must be between 1 and 14")
    data = load_data()
    pred_df = compute_predictions(data["atm_registry"], data["atm_history"], forecast_days=forecast_days)
    rows = [] if pred_df.empty else pred_df[
        ["ID", "Day_Ahead", "Pred_Withdrawals", "Pred_Deposits", "Pred_Balance", "Risk"]
    ].to_dict(orient="records")
    return {"forecast_days": forecast_days, "rows": rows}


@app.get("/alerts")
def alerts(forecast_days: int = 3) -> dict:
    data = load_data()
    pred_df = compute_predictions(data["atm_registry"], data["atm_history"], forecast_days=forecast_days)
    if pred_df.empty:
        return {"alerts": []}

    alert_df = pred_df[pred_df["Risk"] != "OK"].sort_values(["ID", "Day_Ahead"]).groupby("ID").first().reset_index()
    return {"alerts": alert_df[["ID", "ATM_Type", "Day_Ahead", "Pred_Balance", "Risk"]].to_dict(orient="records")}

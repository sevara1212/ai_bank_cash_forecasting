import os
from datetime import datetime, timezone

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.data_loader import load_data
from backend.forecasting import compute_predictions

app = FastAPI(title="AI Bank Cash Forecast API", version="1.0.0")

def parse_frontend_origins(raw_origins: str) -> list[str]:
    value = (raw_origins or "").strip()
    if not value or value == "*":
        return ["*"]

    parsed: list[str] = []
    for origin in (part.strip() for part in value.split(",")):
        if not origin:
            continue
        # Accept common user input without protocol and normalize to https.
        if not origin.startswith(("http://", "https://")):
            origin = f"https://{origin}"
        parsed.append(origin.rstrip("/"))
    return parsed or ["*"]


frontend_origins = os.getenv("FRONTEND_ORIGINS", "*")
allowed_origins = parse_frontend_origins(frontend_origins)
frontend_origin_regex = os.getenv("FRONTEND_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=frontend_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registry columns to include in forecast/alert responses when present.
# We include ALL non-ID columns from the registry so the frontend can pick
# whichever location/name column actually exists in the sheet.
_SKIP_COLS = {"ATM_ID"}  # already present as "ID" in predictions


def _extra_cols(df: pd.DataFrame, base: list[str]) -> list[str]:
    """Return any registry column not already in base."""
    return [c for c in df.columns if c not in base and c not in _SKIP_COLS]


@app.get("/")
def root() -> dict:
    return {"service": "ai-bank-cash-forecast-api", "status": "running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/forecast")
def forecast(forecast_days: int = 3) -> dict:
    if forecast_days < 1 or forecast_days > 14:
        raise HTTPException(status_code=400, detail="forecast_days must be between 1 and 14")
    data = load_data()
    pred_df = compute_predictions(data["atm_registry"], data["atm_history"], forecast_days=forecast_days)
    base = ["ID", "Day_Ahead", "Pred_Withdrawals", "Pred_Deposits", "Pred_Balance", "Risk"]
    cols = base + _extra_cols(pred_df, base)
    rows = [] if pred_df.empty else pred_df[cols].to_dict(orient="records")
    return {"forecast_days": forecast_days, "rows": rows}


@app.get("/alerts")
def alerts(forecast_days: int = 3) -> dict:
    data = load_data()
    pred_df = compute_predictions(data["atm_registry"], data["atm_history"], forecast_days=forecast_days)
    if pred_df.empty:
        return {"alerts": []}

    alert_df = pred_df[pred_df["Risk"] != "OK"].sort_values(["ID", "Day_Ahead"]).groupby("ID").first().reset_index()
    base = ["ID", "ATM_Type", "Day_Ahead", "Pred_Balance", "Risk"]
    cols = base + _extra_cols(alert_df, base)
    return {"alerts": alert_df[cols].to_dict(orient="records")}


@app.get("/registry")
def registry() -> dict:
    """Return ATM registry with all columns — used by frontend to discover label fields."""
    data = load_data()
    reg = data["atm_registry"]
    return {"columns": list(reg.columns), "rows": reg.head(3).to_dict(orient="records")}


@app.get("/history")
def history(days: int = 30) -> dict:
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    data = load_data()
    hist = data["atm_history"].copy()
    hist["Oper_Day"] = pd.to_datetime(hist["Oper_Day"], errors="coerce")
    hist = hist.dropna(subset=["Oper_Day"])
    if hist.empty:
        return {"rows": []}

    cutoff = hist["Oper_Day"].max() - pd.Timedelta(days=days - 1)
    hist = hist[hist["Oper_Day"] >= cutoff]

    daily = (
        hist.groupby("Oper_Day")
        .agg(
            Total_Balance=("Cash_Level_EOD_UZS", "sum"),
            Total_Withdrawals=("Withdrawals_UZS", "sum"),
            Total_Deposits=("Deposits_UZS", "sum"),
        )
        .reset_index()
        .sort_values("Oper_Day")
    )
    daily["Oper_Day"] = daily["Oper_Day"].dt.strftime("%Y-%m-%d")
    return {"rows": daily.to_dict(orient="records")}

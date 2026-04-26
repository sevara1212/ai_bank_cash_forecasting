import pandas as pd
from fastapi.testclient import TestClient

from backend import main as backend_main


def fake_data():
    atm_registry = pd.DataFrame(
        [
            {"ATM_ID": "ATM001", "ATM_Type": "Cash Dispenser", "Max_Capacity_UZS": 1_000_000},
            {"ATM_ID": "ATM002", "ATM_Type": "Full Function", "Max_Capacity_UZS": 2_000_000},
        ]
    )
    atm_history = pd.DataFrame(
        [
            {"ID": "ATM001", "Oper_Day": "2026-04-20", "Cash_Level_EOD_UZS": 500_000, "Withdrawals_UZS": 120_000, "Deposits_UZS": 30_000},
            {"ID": "ATM001", "Oper_Day": "2026-04-21", "Cash_Level_EOD_UZS": 410_000, "Withdrawals_UZS": 100_000, "Deposits_UZS": 20_000},
            {"ID": "ATM001", "Oper_Day": "2026-04-22", "Cash_Level_EOD_UZS": 330_000, "Withdrawals_UZS": 90_000, "Deposits_UZS": 20_000},
            {"ID": "ATM002", "Oper_Day": "2026-04-20", "Cash_Level_EOD_UZS": 1_600_000, "Withdrawals_UZS": 200_000, "Deposits_UZS": 130_000},
            {"ID": "ATM002", "Oper_Day": "2026-04-21", "Cash_Level_EOD_UZS": 1_530_000, "Withdrawals_UZS": 210_000, "Deposits_UZS": 100_000},
            {"ID": "ATM002", "Oper_Day": "2026-04-22", "Cash_Level_EOD_UZS": 1_420_000, "Withdrawals_UZS": 205_000, "Deposits_UZS": 95_000},
        ]
    )
    return {
        "atm_registry": atm_registry,
        "atm_history": atm_history,
        "kassa_registry": pd.DataFrame(),
        "kassa_history": pd.DataFrame(),
    }


def test_health():
    client = TestClient(backend_main.app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_root():
    client = TestClient(backend_main.app)
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "running"


def test_parse_frontend_origins_normalizes_missing_scheme():
    origins = backend_main.parse_frontend_origins("ai-bank-cash-forecasting-xckh.vercel.app, http://localhost:8080/")
    assert origins == [
        "https://ai-bank-cash-forecasting-xckh.vercel.app",
        "http://localhost:8080",
    ]


def test_forecast_and_alerts(monkeypatch):
    monkeypatch.setattr(backend_main, "load_data", fake_data)
    client = TestClient(backend_main.app)

    forecast_res = client.get("/forecast?forecast_days=2")
    assert forecast_res.status_code == 200
    forecast_rows = forecast_res.json()["rows"]
    assert len(forecast_rows) == 4

    alerts_res = client.get("/alerts?forecast_days=2")
    assert alerts_res.status_code == 200
    assert "alerts" in alerts_res.json()

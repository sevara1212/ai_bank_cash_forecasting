from typing import List

import pandas as pd


def _to_int(value: object) -> int:
    return int(float(value))


def detect_risk(row: pd.Series) -> str:
    if pd.isna(row.get("Max_Capacity_UZS")):
        return "UNKNOWN"
    if row["Pred_Balance"] <= 0:
        return "CRITICAL_EMPTY"
    if row["Pred_Balance"] < row["Max_Capacity_UZS"] * 0.2:
        return "LOW_CASH"
    return "OK"


def compute_predictions(atm_registry: pd.DataFrame, atm_history: pd.DataFrame, forecast_days: int = 3) -> pd.DataFrame:
    predictions: List[dict] = []

    for node_id, df_node in atm_history.groupby("ID"):
        df_node = df_node.sort_values("Oper_Day").copy()
        if df_node.empty:
            continue

        last_balance = _to_int(df_node["Cash_Level_EOD_UZS"].iloc[-1])
        recent = df_node.tail(5)

        avg_withdraw = pd.to_numeric(recent["Withdrawals_UZS"], errors="coerce").mean()
        avg_deposit = pd.to_numeric(recent["Deposits_UZS"], errors="coerce").mean()
        trend = pd.to_numeric(recent["Withdrawals_UZS"], errors="coerce").diff().mean()
        if pd.isna(trend):
            trend = 0

        future_balance = last_balance
        for day in range(1, forecast_days + 1):
            predicted_withdraw = max(avg_withdraw + trend * day, 0)
            predicted_deposit = max(avg_deposit, 0)
            future_balance += predicted_deposit - predicted_withdraw
            predictions.append(
                {
                    "ID": node_id,
                    "Day_Ahead": day,
                    "Pred_Withdrawals": int(predicted_withdraw),
                    "Pred_Deposits": int(predicted_deposit),
                    "Pred_Balance": int(future_balance),
                }
            )

    pred_df = pd.DataFrame(predictions)
    if pred_df.empty:
        return pred_df

    pred_df = pred_df.merge(atm_registry, left_on="ID", right_on="ATM_ID", how="left")
    pred_df["Risk"] = pred_df.apply(detect_risk, axis=1)
    return pred_df

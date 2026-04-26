from typing import Dict

import pandas as pd

from backend.config import GIDS, SHEET_ID


def load_sheet(sheet_id: str, gid: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return pd.read_csv(url)


def load_data() -> Dict[str, pd.DataFrame]:
    return {
        "atm_registry": load_sheet(SHEET_ID, GIDS["atm_registry"]),
        "atm_history": load_sheet(SHEET_ID, GIDS["atm_history"]),
        "kassa_registry": load_sheet(SHEET_ID, GIDS["kassa_registry"]),
        "kassa_history": load_sheet(SHEET_ID, GIDS["kassa_history"]),
    }

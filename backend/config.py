import os


SHEET_ID = os.getenv("SHEET_ID", "12YxYgetu4pyqHdbT0NL1NBFiCdGJEo7N")

GIDS = {
    "atm_registry": os.getenv("ATM_REGISTRY_GID", "2053419249"),
    "atm_history": os.getenv("ATM_HISTORY_GID", "913700150"),
    "kassa_registry": os.getenv("KASSA_REGISTRY_GID", "1755061160"),
    "kassa_history": os.getenv("KASSA_HISTORY_GID", "1963259370"),
}

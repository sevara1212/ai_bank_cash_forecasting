# ai_bank_cash_forecasting

Cash forecasting dashboard and notebook deployment bundle.

## Run frontend (static)

```bash
python3 build_site.py
python3 -m http.server 8080 --directory dist
```

## Run Python backend API

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

## Backend development setup

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
pytest -q
```

Useful dev commands:

- `uvicorn backend.main:app --reload --port 8000`
- `pytest -q`

API endpoints:

- `GET /health`
- `GET /forecast?forecast_days=3`
- `GET /alerts?forecast_days=3`

Frontend integration:

- Backend URL used by dashboard JS: `https://ai-bank-cash-forecasting.onrender.com`
- CORS origins env var: `FRONTEND_ORIGINS` (comma-separated URLs)

## Important deployment note

Netlify can host the static frontend (`dist`) but does not run this Python backend directly.
Deploy backend separately (for example Render/Railway/Fly.io), then point frontend calls to that backend URL.

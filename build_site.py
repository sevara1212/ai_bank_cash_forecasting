#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "hackathon.ipynb"
DASHBOARD_HTML = ROOT / "ai_bank_cash_forecasting_dashboard (1).html"
DIST = ROOT / "dist"
NOTEBOOK_OUT = DIST / "notebook-report.html"
INDEX_OUT = DIST / "index.html"


def run_nbconvert() -> bool:
    cmd = [
        "jupyter",
        "nbconvert",
        "--to",
        "html",
        str(NOTEBOOK),
        "--output",
        NOTEBOOK_OUT.name,
        "--output-dir",
        str(DIST),
    ]
    try:
        subprocess.run(cmd, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def write_fallback_notebook_page() -> None:
    NOTEBOOK_OUT.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Notebook Report</title>
  <style>
    body { font-family: system-ui, sans-serif; padding: 2rem; max-width: 760px; margin: 0 auto; }
    code { background: #f2f2f2; padding: 0.15rem 0.35rem; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Notebook report is not generated yet</h1>
  <p>Install Jupyter and run:</p>
  <p><code>jupyter nbconvert --to html hackathon.ipynb --output notebook-report.html --output-dir dist</code></p>
  <p><a href="./index.html">Back to dashboard</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def build() -> None:
    DIST.mkdir(exist_ok=True)
    shutil.copy2(DASHBOARD_HTML, INDEX_OUT)

    ok = run_nbconvert()
    if not ok:
        write_fallback_notebook_page()

    print(f"Build complete: {DIST}")
    print("Start local deploy preview with: python3 -m http.server 8080 --directory dist")


if __name__ == "__main__":
    build()

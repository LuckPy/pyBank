from pathlib import Path


CASH_DIR = Path.home() / ".cashflow"
if not CASH_DIR.exists():
    CASH_DIR.mkdir()


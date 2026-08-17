from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


DATA_PATH = PROJECT_ROOT / "data"
OUTPUT_PATH = PROJECT_ROOT / "output"
DATABASE_PATH = PROJECT_ROOT / "database" / "finance.db"
LOG_PATH = OUTPUT_PATH / "logs" / "finance.log"
LOG_LEVEL = "INFO"
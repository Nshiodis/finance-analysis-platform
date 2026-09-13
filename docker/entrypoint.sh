#!/bin/sh
set -e

python -m finance_analysis.database.init_db

exec uvicorn finance_analysis.api.app:app --host 0.0.0.0 --port 8000
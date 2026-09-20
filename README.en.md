# Finance Analysis Platform

**A financial data analysis platform** — it turns A-share daily price data into a REST API you can call, test and deploy.

> 中文版见 [README.md](README.md)。This is a learning project: it started as plain Pandas scripts and was refactored step by step into a layered service (indicators / risk / portfolio / performance) with logging, configuration management, tests and containerization. The full learning log is in [AGENTS.md](AGENTS.md) (Chinese).

---

## What it does

| Capability | Entry point |
| --- | --- |
| Load price CSVs into SQLite (idempotent, safe to re-run) | `python -m finance_analysis.database.init_db` |
| List symbols / stock metrics / risk metrics | `GET /stocks`, `GET /stocks/{symbol}`, `GET /stocks/{symbol}/risk` |
| Technical indicator series (MA / RSI / MACD) | `GET /stocks/{symbol}/indicators?window=20` |
| Create a portfolio, evaluate it against a benchmark | `POST /portfolios`, `GET /portfolios/{id}/performance` |
| Interactive API docs | http://127.0.0.1:8000/docs |
| Container run with one command | `docker compose up -d --build` |

What is implemented under `src/finance_analysis/analysis/`:

- Returns and cumulative returns
- MA (moving average), RSI (Wilder smoothing), MACD (DIF / DEA / MACD)
- Annualized volatility, max drawdown, Sharpe ratio (1.5% annual risk-free rate by default)
- Portfolio return, annualized return, volatility, Sharpe, benchmark return, excess return

## Tech stack

| Purpose | Choice |
| --- | --- |
| Language | Python 3.13 |
| Data processing | pandas / numpy |
| Web framework | FastAPI + Uvicorn |
| Storage | SQLite (standard library `sqlite3`) |
| Configuration | pydantic-settings (`.env` / `FINANCE_*` environment variables) |
| Tests | pytest + httpx (TestClient) + pytest-cov |
| Type checking | Pyright strict (local stubs for untyped third-party code, see `typings/`) |
| Deployment | Docker multi-stage build + docker-compose |

## Project layout

```text
finance-analysis-platform/
├── src/finance_analysis/
│   ├── api/                  # FastAPI layer: routers / response models / DI / request-log middleware
│   ├── services/             # Business orchestration: StockService / PortfolioService
│   ├── repository/           # Data access: SQLite <-> DataFrame (no business rules here)
│   ├── database/             # DatabaseManager / DatabaseLoader / init_db
│   ├── models/               # Business objects: StockData / StockPool / Portfolio
│   ├── analysis/             # Indicators / risk / benchmark / performance (pure computation)
│   ├── data/                 # Market data download (akshare)
│   ├── visualization/        # Plotting
│   ├── utils/                # Logging and file helpers
│   ├── config.py             # Settings: single source of configuration
│   └── exceptions.py         # Error hierarchy: AppError + subclasses
├── tests/                    # pytest suites (unit / integration / API)
├── data/                     # Source price CSVs
├── docker/entrypoint.sh      # Container entry: load the DB, then exec uvicorn
├── docs/                     # ARCHITECTURE.md (design) / API.md (endpoint reference)
├── typings/                  # Local type stubs (for pyright strict)
├── examples/                 # early practice scripts + DB/analysis demos (not collected by pytest, not type-checked)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml            # Packaging / pytest / pyright configuration
└── .env.example              # Configuration template
```

## Quick start (local)

Prerequisite: Python 3.13.

```powershell
# 0. Make sure `python` really works — it must print a version
python --version                  # expected: Python 3.13.x
# If nothing is printed, or you get "Python was not found", the `python` on your PATH is
# the Microsoft Store alias stub (a no-op executable): `python -m venv .venv` silently
# does nothing. Use the full path of a real interpreter instead, e.g.
#   & "D:\03_Dev\Develop\Tools\Python3.13\python.exe" -m venv .venv

# 1. Create the virtual environment
python -m venv .venv

# 2. Install dependencies, then this project in editable mode
#    (the src layout must be installed, otherwise `import finance_analysis` fails)
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
# Slow network? Add a mirror (the Docker build uses the same one):
#   .venv\Scripts\python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 3. Prepare configuration (.env is gitignored — change settings without touching code)
Copy-Item .env.example .env

# 4. Load the database: create tables + import data/*.csv into database/finance.db
#    (idempotent: re-running never inserts duplicates)
.venv\Scripts\python.exe -m finance_analysis.database.init_db

# 5. Start the service (--reload restarts on code changes; handy while developing)
.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload
```

On Linux / macOS replace `.venv\Scripts\python.exe` with `.venv/bin/python` and `Copy-Item` with `cp`; everything else stays the same.

Verify it works:

```powershell
curl.exe http://127.0.0.1:8000/stocks/600519
# {"symbol":"600519","rows":1455,"latest_close":1377.18,...}

start http://127.0.0.1:8000/docs
```

## Quick start (Docker)

```powershell
docker compose up -d --build     # build the image and start the container
docker compose ps                # wait until STATUS shows healthy
curl.exe http://127.0.0.1:8000/docs

docker compose down              # stop and remove the container (the finance-data volume stays)
docker compose down -v           # also remove the volume: data is gone, the next start re-loads it
```

What happens inside: `docker/entrypoint.sh` first runs `python -m finance_analysis.database.init_db`
to load the data, then `exec uvicorn ... --host 0.0.0.0 --port 8000` to serve. The SQLite file lives
on the `finance-data` volume (mounted at `/app/database`), so `down` followed by `up` keeps your data.

> Machine-specific note: on this machine (Rancher Desktop with a broken Windows ↔ WSL bridge) docker
> commands must run inside the VM:
>
> ```powershell
> wsl -d rancher-desktop -u root -- sh -c "cd /mnt/d/03_Dev/Develop/Projects/finance-analysis-platform && docker compose up -d --build"
> ```

## Calling the API

```powershell
# Which symbols are available
curl.exe http://127.0.0.1:8000/stocks

# One stock: rows / latest close / total return / volatility / Sharpe / max drawdown
# (optional date filters)
curl.exe "http://127.0.0.1:8000/stocks/600519?start=2024-01-01&end=2024-12-31"

# Technical indicator series: window applies to MA and RSI; MACD is fixed at 12/26/9
curl.exe "http://127.0.0.1:8000/stocks/600519/indicators?window=20"

# Create a portfolio (weights must sum to 1)
curl.exe -X POST http://127.0.0.1:8000/portfolios -H "Content-Type: application/json" -d "{\"weights\":{\"600519\":0.4,\"000858\":0.3,\"300750\":0.3}}"

# Check its performance (use the id returned above)
curl.exe http://127.0.0.1:8000/portfolios/38/performance
```

> In Windows PowerShell `curl` is an alias for `Invoke-WebRequest` with incompatible arguments — always use `curl.exe`.

Full endpoint list, parameters, real responses and error codes: [docs/API.md](docs/API.md) (Chinese).

## Tests and type checking

```powershell
# All tests: 59 cases (unit / integration / API). Core-layer coverage: 99%
.venv\Scripts\python.exe -m pytest

# API tests only
.venv\Scripts\python.exe -m pytest tests/test_api.py -v

# Strict type checking: 0 errors
.venv\Scripts\python.exe -m pyright --pythonpath .venv\Scripts\python.exe src tests
```

Three things worth knowing:

- Tests are isolated: `tests/conftest.py` points `settings.database_path` at a temporary database and loads it from the real CSVs, so running tests never touches your dev database
- The standalone `pyright` needs `--pythonpath`, otherwise it cannot resolve third-party packages and reports hundreds of false errors
- Set `$env:MPLBACKEND='Agg'` before running any plotting script (headless backend, no pop-up windows)

## Configuration

All configuration lives in [`src/finance_analysis/config.py`](src/finance_analysis/config.py): defaults are in code, and `.env` or environment variables override them.

| Environment variable | Default | Meaning |
| --- | --- | --- |
| `FINANCE_ENVIRONMENT` | `development` | `development` / `testing` / `production`; anything else fails fast at startup |
| `FINANCE_LOG_LEVEL` | `INFO` | `DEBUG` < `INFO` < `WARNING` < `ERROR` |
| `FINANCE_DATABASE_PATH` | `database/finance.db` | SQLite file path |
| `FINANCE_DATA_PATH` | `data` | Directory holding the price CSVs |
| `FINANCE_OUTPUT_PATH` | `output` | Directory for generated artifacts |
| `FINANCE_LOG_PATH` | `output/logs/finance.log` | Log file path |

Precedence: code defaults < `.env` < real environment variables < explicit arguments.
The `FINANCE_` prefix is deliberate: a bare system variable such as `DATABASE_PATH` cannot hijack this project's configuration.

## Where the data comes from

Four daily CSVs live in `data/`:

| File | Instrument | Role |
| --- | --- | --- |
| `600519.csv` | Kweichow Moutai | analysis target |
| `000858.csv` | Wuliangye | analysis target |
| `300750.csv` | CATL | analysis target |
| `000300.csv` | CSI 300 index | benchmark for portfolio performance |

Two things to note:

- The first three have 9 columns, `000300.csv` has only 7. The table schema is declared in code (`DatabaseManager.create_stock_price_table()`), so it never depends on which CSV is read first
- To add a stock: drop `{symbol}.csv` into `data/` and run `init_db` again — `INSERT OR IGNORE` plus `UNIQUE(symbol, date)` makes it safe

## Documentation

| Document | What's inside |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers, full request path, database design, key decisions (Chinese) |
| [docs/API.md](docs/API.md) | Endpoint reference, parameters, real responses, error codes (Chinese) |
| [AGENTS.md](AGENTS.md) | Learning roadmap (Day1–Day35) and daily progress (Chinese) |
| http://127.0.0.1:8000/docs | Auto-generated interactive docs — click and try |

> The detailed docs are currently written in Chinese; the README is bilingual.

---

Learning project, updated continuously.

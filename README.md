# Finance Analysis Platform

> **中文** · [English](README.en.md)

> **状态**：v1.0.0 已封版（2026-09-20），当前为**维护模式**。想回来接着做看 [docs/ROADMAP.md](docs/ROADMAP.md)（含复活流程），面试/实习讲述用 [docs/PROJECT_STORY.md](docs/PROJECT_STORY.md)。

**金融数据分析学习平台** —— 把 A 股日线行情变成一套可调用、可测试、可部署的 REST API。

这是一个从「Pandas 脚本」一路重构出来的学习项目：先做数据分析（指标 / 风险 / 组合 / 绩效），
再做工程化（分层架构 / 异常体系 / 日志 / 配置 / 测试 / 容器化）。
完整学习路线与每日进度记录在 [AGENTS.md](AGENTS.md)。

---

## 功能一览

| 能力 | 入口 |
| --- | --- |
| CSV 行情灌库（幂等，可重复执行） | `python -m finance_analysis.database.init_db` |
| 股票列表 / 行情指标 / 风险指标 | `GET /stocks`、`GET /stocks/{symbol}`、`GET /stocks/{symbol}/risk` |
| 技术指标序列（MA / RSI / MACD） | `GET /stocks/{symbol}/indicators?window=20` |
| 组合创建 + 绩效评价（含沪深300 基准对比） | `POST /portfolios`、`GET /portfolios/{id}/performance` |
| 交互式接口文档 | http://127.0.0.1:8000/docs |
| 一条命令容器化启动 | `docker compose up -d --build` |

已实现的计算能力（`src/finance_analysis/analysis/`）：

- 收益率、累计收益率
- MA（移动平均）、RSI（Wilder 平滑）、MACD（DIF / DEA / MACD）
- 年化波动率、最大回撤、夏普比率（年化无风险利率默认 1.5%）
- 组合收益、年化收益、波动率、夏普、基准收益、超额收益

## 技术栈

| 用途 | 选型 |
| --- | --- |
| 语言 | Python 3.13 |
| 数据处理 | pandas / numpy |
| Web 框架 | FastAPI + Uvicorn |
| 存储 | SQLite（标准库 `sqlite3`） |
| 配置 | pydantic-settings（`.env` / `FINANCE_*` 环境变量） |
| 测试 | pytest + httpx（TestClient）+ pytest-cov |
| 类型检查 | Pyright strict（三方库缺注解的部分用本地 stub 补，见 `typings/`） |
| 部署 | Docker 多阶段构建 + docker-compose |

## 目录结构

```text
finance-analysis-platform/
├── src/finance_analysis/
│   ├── api/                  # FastAPI 层：路由 / 响应模型 / 依赖注入 / 请求日志中间件
│   ├── services/             # 业务编排：StockService / PortfolioService
│   ├── repository/           # 数据访问：SQLite ↔ DataFrame（不写业务规则）
│   ├── database/             # DatabaseManager / DatabaseLoader / init_db
│   ├── models/               # 业务对象：StockData / StockPool / Portfolio
│   ├── analysis/             # 指标 / 风险 / 基准 / 绩效（纯计算）
│   ├── data/                 # 行情下载（akshare）
│   ├── visualization/        # 绘图
│   ├── utils/                # 日志与文件工具
│   ├── config.py             # Settings：集中配置
│   └── exceptions.py         # 异常体系：AppError + 子类
├── tests/                    # pytest 测试（单元 / 集成 / 接口）
├── data/                     # 行情源数据 CSV
├── docker/entrypoint.sh      # 容器入口：先灌库，再 exec uvicorn
├── docs/                     # ARCHITECTURE.md（架构）/ API.md（接口手册）
├── typings/                  # 本地类型 stub（pyright strict 用）
├── examples/                 # 早期练习脚本 + 数据库/分析 demo（不参与 pytest 与 pyright）
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml            # 打包 / pytest / pyright 配置
└── .env.example              # 配置模板
```

## 快速开始（本地）

前置：Python 3.13。

```powershell
# 0. 先确认 python 真的能用（能打印版本号再往下走）
python --version                  # 期望：Python 3.13.x
# 如果没有任何输出、或提示 "Python was not found"，说明命中的是 Microsoft Store 的
# 别名桩（一个空壳 exe，执行后静默退出）。换成安装目录里的完整路径，例如：
#   & "D:\03_Dev\Develop\Tools\Python3.13\python.exe" -m venv .venv

# 1. 建虚拟环境
python -m venv .venv

# 2. 装依赖，并把本项目按 editable 方式装进环境（src 布局必须装，否则 import 不到 finance_analysis）
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
# 国内网络慢的话，给 pip 加镜像源（Docker 构建里用的就是这个）：
#   .venv\Scripts\python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 3. 准备配置（.env 不入库，改配置不用改代码）
Copy-Item .env.example .env

# 4. 灌库：建表 + 把 data/*.csv 写进 database/finance.db（幂等，重复执行不会写重复数据）
.venv\Scripts\python.exe -m finance_analysis.database.init_db

# 5. 启动服务（--reload = 改代码自动重启，开发期用它）
.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload
```

Linux / macOS：把 `.venv\Scripts\python.exe` 换成 `.venv/bin/python`、`Copy-Item` 换成 `cp` 即可，其余命令相同。

启动后验证：

```powershell
curl.exe http://127.0.0.1:8000/stocks/600519
# {"symbol":"600519","rows":1455,"latest_close":1377.18,...}

start http://127.0.0.1:8000/docs
```

## 快速开始（Docker）

```powershell
docker compose up -d --build     # 构建镜像 + 起容器
docker compose ps                # 等 STATUS 变成 healthy
curl.exe http://127.0.0.1:8000/docs

docker compose down              # 停止并删除容器（数据卷 finance-data 保留）
docker compose down -v           # 连数据卷一起删：数据没了，下次启动重新灌库
```

容器里发生了什么：`docker/entrypoint.sh` 先跑 `python -m finance_analysis.database.init_db` 灌库，
再用 `exec uvicorn ... --host 0.0.0.0 --port 8000` 起服务；SQLite 文件落在 `finance-data` 数据卷上
（容器内路径 `/app/database`），所以 `down` 之后 `up`，数据还在。

> 本机特例：Rancher Desktop 的 Windows ↔ WSL 桥是坏的，docker 命令要进虚拟机执行：
>
> ```powershell
> wsl -d rancher-desktop -u root -- sh -c "cd /mnt/d/03_Dev/Develop/Projects/finance-analysis-platform && docker compose up -d --build"
> ```

## 调用接口

```powershell
# 有哪些股票
curl.exe http://127.0.0.1:8000/stocks

# 单只股票：行数 / 最新收盘价 / 累计收益 / 波动率 / 夏普 / 最大回撤（可加日期区间）
curl.exe "http://127.0.0.1:8000/stocks/600519?start=2024-01-01&end=2024-12-31"

# 技术指标序列：window 同时作用于 MA 和 RSI，MACD 固定 12/26/9
curl.exe "http://127.0.0.1:8000/stocks/600519/indicators?window=20"

# 创建组合（权重和必须为 1）
curl.exe -X POST http://127.0.0.1:8000/portfolios -H "Content-Type: application/json" -d "{\"weights\":{\"600519\":0.4,\"000858\":0.3,\"300750\":0.3}}"

# 查组合绩效（id 用创建接口返回的值）
curl.exe http://127.0.0.1:8000/portfolios/38/performance
```

> Windows PowerShell 里 `curl` 是 `Invoke-WebRequest` 的别名，参数不兼容，请写 `curl.exe`。

完整的接口清单、参数说明、真实响应和错误码表见 [docs/API.md](docs/API.md)。

## 测试与类型检查

```powershell
# 全部测试：59 个用例（单元 / 集成 / 接口三层），核心层覆盖率 99%
.venv\Scripts\python.exe -m pytest

# 只跑接口测试
.venv\Scripts\python.exe -m pytest tests/test_api.py -v

# 严格类型检查：0 错误
.venv\Scripts\python.exe -m pyright --pythonpath .venv\Scripts\python.exe src tests
```

三个容易踩的点：

- 测试自带隔离：`tests/conftest.py` 会把 `settings.database_path` 指向临时库、从真实 CSV 灌数据，跑测试不会动开发库
- 官方 `pyright` 必须带 `--pythonpath`，不带就解析不到第三方包，会报出成百上千条假错误
- 涉及绘图的脚本先设 `$env:MPLBACKEND='Agg'`（无窗口后端，避免弹窗阻塞）

## 配置

配置集中在 [`src/finance_analysis/config.py`](src/finance_analysis/config.py)：默认值写在代码里，可用 `.env` 或环境变量覆盖。

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `FINANCE_ENVIRONMENT` | `development` | `development` / `testing` / `production`；填别的启动即报错 |
| `FINANCE_LOG_LEVEL` | `INFO` | `DEBUG` < `INFO` < `WARNING` < `ERROR` |
| `FINANCE_DATABASE_PATH` | `database/finance.db` | SQLite 文件路径 |
| `FINANCE_DATA_PATH` | `data` | 行情 CSV 目录 |
| `FINANCE_OUTPUT_PATH` | `output` | 图表等产物目录 |
| `FINANCE_LOG_PATH` | `output/logs/finance.log` | 日志文件路径 |

取值优先级：代码默认值 < `.env` < 真实环境变量 < 显式传参。
前缀 `FINANCE_` 是防呆设计：裸的 `DATABASE_PATH` 之类系统变量劫持不了本项目配置。

## 数据从哪来

`data/` 下是 4 个日线 CSV：

| 文件 | 标的 | 用途 |
| --- | --- | --- |
| `600519.csv` | 贵州茅台 | 分析标的 |
| `000858.csv` | 五粮液 | 分析标的 |
| `300750.csv` | 宁德时代 | 分析标的 |
| `000300.csv` | 沪深300指数 | 组合绩效的基准 |

注意两点：

- 前三个 CSV 是 9 列，`000300.csv` 只有 7 列。表结构由代码显式声明（`DatabaseManager.create_stock_price_table()`），不依赖先读到哪个 CSV
- 想加新股票：把 `{股票代码}.csv` 放进 `data/` 重新跑一次 `init_db` 即可 —— `INSERT OR IGNORE` + `UNIQUE(symbol, date)` 保证重复执行安全

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 分层架构、一次请求的完整链路、数据库设计、关键设计决策 |
| [docs/API.md](docs/API.md) | 接口清单、参数说明、真实示例、错误码表 |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 封版说明、回来时的复活流程、候选项、"发下一个版本"的流程 |
| [docs/PROJECT_STORY.md](docs/PROJECT_STORY.md) | 一页纸项目讲述（面试 / 实习用）：三档讲法、关键决策、踩坑、可背数字 |
| [AGENTS.md](AGENTS.md) | 学习路线（Day1–Day35）与每日进度记录 |
| http://127.0.0.1:8000/docs | FastAPI 自动生成的交互式文档，可以直接点着试 |

---

学习项目，持续更新中。

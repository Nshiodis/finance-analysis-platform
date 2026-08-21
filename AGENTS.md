# AGENTS.md

## 项目简介

金融数据分析学习平台（暑期导师式每日任务）。当前完成到 **Day27：RESTful API 设计**（`APIRouter` 按资源拆分，`/stocks` 列表 + `/stocks/{symbol}`）。
下一步 **Day28：金融分析 API**（完整路线见文末"学习路线规划"）。

## 技术栈

- Python 3.13 + Pandas + Matplotlib + SQLite（标准库 `sqlite3`）
- FastAPI + Uvicorn（API 服务，`.venv` 已安装）
- pytest + httpx（接口自动化测试，`.venv` 已安装）
- 虚拟环境：`.venv`（用 `.venv\Scripts\python.exe` 运行）
- 包：`finance_analysis`（src 布局，editable install）

## 当前结构

```
src/finance_analysis/
├── config.py           # 集中配置：PROJECT_ROOT / DATA_PATH / OUTPUT_PATH / DATABASE_PATH / LOG_PATH / LOG_LEVEL
├── exceptions.py       # 异常体系（AppError 基类 + 4 个子类，携带 status_code / code）
├── api/                # FastAPI 应用（app.py：include_router + 统一异常处理器 + 旧路径 deprecated；routers/stocks.py：APIRouter；dependencies.py：依赖注入；schemas.py：响应模型）
├── services/           # StockService（业务编排：取数 → 异常判断 → 算指标 → 组结果）
├── models/             # StockData / StockPool / Portfolio（业务对象）
├── repository/         # StockRepository（数据访问层，业务层不直接碰 SQLite）
├── database/           # manager.py（DatabaseManager）/ loader.py（DatabaseLoader）
├── analysis/           # indicators / risk / evaluation / benchmark
├── data/               # download_stock.py
├── utils/              # logger.py（setup_logging）/ utils.py（load_csv / save_csv / save_plot）
└── visualization/      # 绘图（函数内部有 plt.show()，自动化测试需 MPLBACKEND=Agg）
```

## 进度记录

- Day1-19：Pandas 基础 → 技术指标 → 风险 → 组合 → 绩效（详见 git log）
- Day20：SQLite 持久化（DatabaseManager / DatabaseLoader，`stock_price` 表，symbol+date 唯一约束）
- Day21：数据访问层解耦（StockRepository；`StockData.from_dataframe/from_database`、`StockPool.from_database`）
- Day22（已完成）：分层重构 + `config.py` + `utils/logger.py` + print→logging + 异常处理 + 产物不入库
  - 提交：`refactor: restructure project into layered architecture`
  - `chore: stop tracking generated database and output artifacts`
  - `feat: add config management and logging system`
- Day23（已完成）：FastAPI 服务化（`api/app.py`：`GET /stock/{symbol}` 返回 symbol / rows / latest_close / total_return / volatility / sharpe / max_drawdown；不存在的股票返回 404）
  - 提交：`feat: add FastAPI service with stock metrics endpoint`
- Day24（已完成）：响应模型与查询参数（`api/schemas.py` 定义 `StockResponse`；`?start=&end=` 日期区间筛选穿透到 SQL 层；`exceptions.py` 区分"股票不存在"与"区间无数据"；`tests/test_api.py` 改为 pytest 接口测试）
  - 提交：`feat: add response model and date range query for stock API`
- Day25（已完成）：Service 层与业务逻辑分离（新增 `services/stock_service.py`：`StockService.get_stock_metrics` 承接取数/空判断/算指标/组 dict 的编排；`app.py` 瘦身为"收请求、转参数、调 Service、回 Response Model"；异常语义与接口行为不变）
  - 提交：`refactor: extract service layer for stock business logic`
- Day26（已完成）：统一异常与统一响应（`AppError` 基类携带 `status_code`/`code`；`InvalidDateRangeError` 在 Service 校验 `start > end`；`DatabaseError` 在 Repository 包装 `sqlite3.Error`；`app.py` 注册 `AppError` / `RequestValidationError` 处理器并删光 try/except；错误响应统一为 `{"code", "message"}`）
  - 提交：`feat: unify error handling with code/message responses`
- Day27（已完成）：RESTful API 设计（`APIRouter(prefix="/stocks", tags=["stocks"])` 按资源拆分；新增 `GET /stocks` 列表接口，数据链 DatabaseManager.query_symbols → StockRepository.get_all_symbols → StockService.list_stocks；`Depends(get_stock_service)` 依赖注入；旧路径 `/stock/{symbol}` 保留并标 `deprecated=True`；测试 8 个全绿）
  - 提交：`feat: add RESTful stocks router and list endpoint`
- Review（2026-08-20 已完成）：Day20–27 分层架构整体复盘（代码走查 + 逐层拆解），产出 6 篇笔记：Service 业务 / Router 路由 / Repository 仓库 / DatabaseManager 数据库管理器 / Exceptions 异常 / Models 模型，位于 `D:\Notes\Learning_Log\Finance_Analysis\review\md格式\`
  - 核心结论：主线骨架 Router → Service → Repository → Database 成立；每层"是什么 / 为什么 / 纪律"已梳理（如 Service 只编排不碰 SQL、Repository 统一翻译 sqlite3.Error、DatabaseManager 参数化查询防注入），为 Day28 新增分析接口打底

## 约定与注意事项

- 用户是学生，**中文交流**；每日一课，**先讲清楚再做**；用户自己写核心代码并贴回来核对；避免重复布置已完成的内容
- 测试在 `tests/test_*.py`：原有为脚本式（`$env:MPLBACKEND='Agg'` 后逐个 `python` 运行）；`test_api.py` 为 pytest 式（`.venv\Scripts\python.exe -m pytest tests/test_api.py -v`）
- 日志：程序入口调用一次 `finance_analysis.utils.logger.setup_logging()`
- API 启动：`.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload`（交互文档 http://127.0.0.1:8000/docs）
- 数据库：`database/finance.db` 不入库，新环境用 DatabaseLoader 从 `data/*.csv` 重建
- 输出产物（`output/`、`*.png`、`*.log`）不入库（.gitignore 已配置）
- 学习笔记在 `D:\Notes`（Obsidian）：每日笔记 `Learning_Log\Finance_Analysis\2026-08\`，索引 `Learning_Log\Finance_Analysis\_索引.md`，FastAPI 主题笔记 `Programming\FastAPI\`，分层架构 Review 笔记 `Learning_Log\Finance_Analysis\review\md格式\`

## Day24（已完成）

- Pydantic 响应模型：`api/schemas.py` 定义 `StockResponse`（`response_model=` + 自动文档）
- 查询参数：`GET /stock/{symbol}?start=&end=` 日期区间筛选，参数穿透 API → StockData → StockRepository → DatabaseManager（SQL 动态拼接，`start/end` 转 `isoformat()` 绑定）
- 业务异常：`exceptions.py` 的 `StockNotFoundError` / `StockNoDataError`（继承 ValueError）区分两种 404 语义
- 接口测试：`tests/test_api.py`（pytest + TestClient，fixture + parametrize，覆盖正常 / 区间 / 空区间 / 非法日期 / 不存在共 5 个场景）

## Day25（已完成）

- Service 层：新增 `services/stock_service.py`，`StockService` 构造时持有 `StockRepository(db_path=DATABASE_PATH)`（依赖显式化）
- 方法 `get_stock_metrics(symbol, start, end) -> dict`：取数 → 空判断（先查区间、空再查全量，区分 `StockNotFoundError` / `StockNoDataError`）→ `calculate_return()` → 组装与 `StockResponse` 字段一致的 dict
- 路由瘦身：`app.py` 只做"收请求、转参数、调 Service、回 Response Model"；`try/except` 暂留路由层（Day26 统一异常时收编）
- 验收：`GET /stock/600519` 行为不变，5 个 pytest 接口测试全绿

## Day26（已完成）

- 异常体系：`exceptions.py` 新增 `AppError(ValueError)` 基类（类属性 `status_code` / `code`），四个子类：`StockNotFoundError`(404/STOCK_NOT_FOUND)、`StockNoDataError`(404/STOCK_NO_DATA)、`InvalidDateRangeError`(422/INVALID_DATE_RANGE)、`DatabaseError`(500/DATABASE_ERROR)
- 业务校验：`StockService.get_stock_metrics` 开头校验 `start > end` 抛 `InvalidDateRangeError`（fail fast）
- 数据层包装：`StockRepository.get_stock` 捕获 `sqlite3.Error` → `raise DatabaseError(...) from exc`（异常链保留根因，message 不暴露内部细节）
- 统一响应：`app.py` 注册 `@app.exception_handler(AppError)` 与 `RequestValidationError` 处理器，路由删光 try/except；所有错误返回 `{"code": ..., "message": ...}`
- 测试：`test_api.py` 断言改为 `code` 全等 + `message` 子串，新增倒挂区间用例，6 个用例全绿

## Day27（已完成）

- REST 语义：资源名词复数 `/stocks` → `/stocks/{symbol}`，查询参数只做过滤
- `api/routers/stocks.py`：`APIRouter(prefix="/stocks", tags=["stocks"])`，端点 `GET /stocks`（列表）与 `GET /stocks/{symbol}`（指标）
- 依赖注入：`api/dependencies.py` 定义 `get_stock_service()`，路由签名 `service: StockService = Depends(get_stock_service)`，避免循环 import，为 Day30 mock 单测铺路
- 数据链：`DatabaseManager.query_symbols()`（`SELECT DISTINCT symbol ...`）→ `StockRepository.get_all_symbols()`（包 `DatabaseError`）→ `StockService.list_stocks()`
- 兼容：旧路径 `/stock/{symbol}` 保留并标 `deprecated=True`，/docs 自动标记废弃
- 测试：主体用例切到 `/stocks/{symbol}`，新增列表与旧路径兼容用例，8 个全绿

## 学习路线规划（Day25–Day35）

> 阶段定位：Day1–19 是"我会什么"，Day20–24 是"我怎么把它组织起来"，Day25–35 是"把它做成别人能调用、测试、部署的软件"。
> 原则：**不回头堆金融指标，不做前端**；每个接口/每层改动当天补 pytest + git 提交 + Obsidian 笔记。

主线骨架（所有接口都长这样）：

```
Router → Service → Repository → Database
```

### 逐日安排

- **Day25 Service 层与业务逻辑分离**（已完成）：新增 `services/`（如 `StockService`），把编排逻辑从 `app.py` 挪进 Service；`app.py` 只做"收请求、转参数、回 Response Model"。验收：`GET /stock/600519` 行为不变，配套单测通过。
- **Day26 统一异常与统一响应**（已完成）：扩展 `exceptions.py`（`InvalidDateRangeError` / `DatabaseError` 等），用 FastAPI 异常处理器统一转 JSON（`code` + `message`），去掉接口里散落的 try/except。验收：所有错误响应的结构统一。
- **Day27 RESTful API 设计**（已完成）：学 REST 资源语义；用 `APIRouter` 按资源拆分路由；v1.0 前统一资源命名为复数 `/stocks/{symbol}`（旧路径可先保留兼容）；补 `GET /stocks` 列表。验收：`/docs` 结构清晰、无重复代码。
- **Day28 金融分析 API**：把 Day17–19 能力暴露成接口：`GET /stocks/{symbol}/risk`（收益/波动/回撤/Sharpe）、`/indicators?window=20`（MA/RSI/MACD）。验收：每个新接口都有 pytest 覆盖。
- **Day29 Portfolio API（含持久化）**：新增 portfolio 表 + `PortfolioRepository` + `PortfolioService`；`POST /portfolios`（请求体 = 权重 dict）、`GET /portfolios/{id}/performance`（组合收益/年化/波动/Sharpe/Benchmark/Excess Return）。验收：组合可入库、可查绩效，接口测试全绿。
- **Day30 测试体系系统化**：测试金字塔——单元（Service，mock Repository）→ 集成（Repository 用临时数据库）→ API（TestClient）；fixture / monkeypatch / mock；引入覆盖率统计。验收：核心层覆盖率 ≥ 70%。
- **Day31 日志与可观测性**：请求日志中间件（method / path / status / 耗时）；分层日志（INFO 查询参数、WARNING 未命中、ERROR 数据库失败）；不记录敏感信息。验收：一条请求在日志里可完整追踪。
- **Day32 配置与环境管理**：引入 pydantic-settings + `.env`；按 development / testing / production 区分配置；测试用独立临时数据库。验收：改环境变量即可切换环境，代码里无硬编码路径。
- **Day33 Docker 化**：Dockerfile（多阶段构建）+ docker-compose。目标：`docker compose up` → `/docs` 可访问。验收：新环境一条命令启动。
- **Day34 项目文档**：README.md（项目是什么 / 如何运行 / 如何测试）+ ARCHITECTURE.md（分层与数据流图）+ API.md（接口清单与示例）。验收：照着文档能在新环境跑起来。
- **Day35 工程 Review 与 v1.0**：代码走查（重复 / 命名 / 注解 / 异常 / 日志 / 测试 / 配置 / 文档）→ 全量 pytest → 打 tag `v1.0.0`。验收：checklist 全过、Git clean。

### 贯穿原则

- 每日一课：先讲清楚再做；核心代码由用户自己写、贴回来核对
- 每天结束时三件套：pytest 全绿 + git commit + Obsidian 笔记（日志 + 主题）
- 一切为"可调用、可测试、可部署"服务

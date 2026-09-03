# AGENTS.md

## 项目简介

金融数据分析学习平台。当前完成到 **Day31：日志与可观测性**（请求日志中间件 + request_id 全链路追踪 + 分层日志）。
下一步 **Day32：配置与环境管理**（完整路线见文末"学习路线规划"）。

## 开始任务前必读

- 每次开始任务（包括新对话）前，先读取同目录的 `AGENTS.local.md`——本机路径、笔记位置、协作方式等个人上下文都写在那里（该文件已被 .gitignore 忽略，不会提交）。

## 技术栈

- Python 3.13 + Pandas + Matplotlib + SQLite（标准库 `sqlite3`）
- FastAPI + Uvicorn（API 服务，`.venv` 已安装）
- pytest + httpx + pytest-cov（单元/集成/接口测试与覆盖率，`.venv` 已安装）
- 虚拟环境：`.venv`（用 `.venv\Scripts\python.exe` 运行）
- 包：`finance_analysis`（src 布局，editable install）

## 当前结构

```
src/finance_analysis/
├── config.py           # 集中配置：PROJECT_ROOT / DATA_PATH / OUTPUT_PATH / DATABASE_PATH / LOG_PATH / LOG_LEVEL
├── exceptions.py       # 异常体系（AppError 基类 + 4 个子类，携带 status_code / code）
├── api/                # FastAPI 应用（app.py：include_router + 统一异常处理器 + 旧路径 deprecated；middleware.py：请求日志中间件；routers/stocks.py / portfolios.py：APIRouter；dependencies.py：依赖注入；schemas.py：响应模型）
├── services/           # StockService / PortfolioService（业务编排）
├── models/             # StockData / StockPool / Portfolio（业务对象）
├── repository/         # StockRepository / PortfolioRepository（数据访问层，业务层不直接碰 SQLite）
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
- Day28（已完成）：金融分析 API（新增 `GET /stocks/{symbol}/risk`（收益/波动/回撤/Sharpe）与 `GET /stocks/{symbol}/indicators?window=20`（MA/RSI/MACD 序列）；`schemas.py` 新增 `RiskResponse`/`IndicatorPoint`/`IndicatorsResponse`；Service 抽取 `_get_stock_data()` 共用“取数 + 空判断”；`window: int = Query(20, ge=1)` 声明式校验；测试 14 个全绿）
  - 提交：`feat: add risk and indicators analysis API`
- Review（2026-08-20 已完成）：Day20–27 分层架构整体复盘（代码走查 + 逐层拆解），产出 6 篇笔记：Service 业务 / Router 路由 / Repository 仓库 / DatabaseManager 数据库管理器 / Exceptions 异常 / Models 模型
  - 核心结论：主线骨架 Router → Service → Repository → Database 成立；每层"是什么 / 为什么 / 纪律"已梳理（如 Service 只编排不碰 SQL、Repository 统一翻译 sqlite3.Error、DatabaseManager 参数化查询防注入），为 Day28 新增分析接口打底
- 类型检查（2026-08-24 已完成）：Pylance strict 全量标红修复（616 → 0 error）
  - 提交：`chore: fix Pylance strict type errors with annotations and local stubs`
  - 手法：全量补参数/返回注解（不改业务逻辑、不改变量名）；`calculate_rsi`/`StockData.calculate_rsi` 返回类型修正为 `pd.Series`；`Portfolio.calculate_return`、`DatabaseManager.insert_portfolio` 用 assert 收窄 `None`；测试 fixture 的 `TestClient` 声明为 `httpx.Client`（绕开 pyright 对 starlette 重载的 Unknown）
  - 依赖：pandas 3.x 不再内置类型标注 → requirements 增加 `pandas-stubs`；matplotlib（`**kwargs: Unknown`）与 akshare（无 stub）→ 本地 stub `typings/`（matplotlib.pyplot / matplotlib.figure / akshare），业务代码零 `# pyright: ignore`；以后新增 `plt.*` 用法需同步在 `typings/matplotlib/pyplot.pyi` 补一行
  - 配置：pyproject.toml 显式声明 `[tool.pyright] typeCheckingMode="strict"` + `stubPath="typings"`；不提交 pyrightconfig.json（Pylance 走 VS Code strict 设置）
  - 环境：`.venv` editable 安装曾指向旧路径，已 `pip install -e .` 修复；pytest 无需 PYTHONPATH 即可运行
  - 补充（stub 质量审查）：提交 `chore: pin pyright strict config and refine local type stubs`；stub 返回值尽量真实类型（Text/Legend/Line2D/BarContainer/PathCollection…），保留 Any 仅限三类——pandas Index/Series 无法装进 matplotlib ArrayLike 的数据参数、Artist 动态属性 kwargs、`gca()`（真实 Axes.set_major_formatter 参数无注解）；akshare 签名与 1.18.70 对齐；社区 matplotlib-stubs 实测更差（strict 下 20 错），不采用
- Day29（已完成）：Portfolio API（含持久化）（新增 portfolio 表，weights 存 JSON 列；PortfolioRepository 管 JSON 编解码 + 自增 id；PortfolioService 校验权重（空/负/和≠1 → 422）→ 组装 Portfolio（date_index() 日期对齐）→ PerformanceEvaluator 算绩效；`POST /portfolios`（201）+ `GET /portfolios/{id}/performance`；测试 19 个全绿）
  - 提交：`feat: add portfolio API with persistence`
- Day30（已完成）：测试体系系统化（测试金字塔落地：单元（Service + mock）×9、集成（Repository + tmp_path 临时库）×9、API ×19，共 37 个全绿；核心层覆盖率 89% → 93%（pytest-cov + pyproject 配置）；测试抓到真 bug：pd.read_sql 把 sqlite3.Error 重包为 pandas.errors.DatabaseError，两个仓库补 except；类型纪律：mock 用 cast(Any, ...) 读取侧收口、assert x is not None 收窄）
  - 提交：`fix: catch pandas DatabaseError in repositories` / `test: add unit and integration tests with coverage`
- Day31（已完成）：日志与可观测性（新增 `api/middleware.py` 请求日志中间件记录 method/path(含 query)/status/耗时；`utils/logger.py` 新增 `request_id_var`（ContextVar，default "-"）与 `RequestIdFormatter`，日志格式带 `[request_id]`，同请求链路自动共享同一 id；分层日志：Service INFO 查询参数 / WARNING 未命中、Repository ERROR 记录数据库根因；不记录敏感信息：中间件不碰 body/header，组合只记 id 不记 weights；测试新增 10 个 → 47 全绿、覆盖率 93%、pyright strict 0 错误）
  - 提交：`feat: add request logging middleware with request_id tracing`

## 约定与注意事项

- 测试在 `tests/test_*.py`：原有为脚本式（`$env:MPLBACKEND='Agg'` 后逐个 `python` 运行）；`test_api.py` 为 pytest 式（`.venv\Scripts\python.exe -m pytest tests/test_api.py -v`）
- 类型检查：项目启用 Pylance/Pyright strict（pyproject `typeCheckingMode = "strict"`）；所有新增代码（含教学示例与测试代码）必须通过 strict 检查，业务代码保持零 `# pyright: ignore`；测试里 mock 用标准写法（如 `typing.cast(Any, MagicMock())`），不要用 `# type: ignore` 绕过
- 日志：程序入口调用一次 `finance_analysis.utils.logger.setup_logging()`
- API 启动：`.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload`（交互文档 http://127.0.0.1:8000/docs）
- 数据库：`database/finance.db` 不入库，新环境用 DatabaseLoader 从 `data/*.csv` 重建
- 输出产物（`output/`、`*.png`、`*.log`）不入库（.gitignore 已配置）
- 笔记要求：每天写 Obsidian 笔记（日志 + 主题）时必须包含当天知识点，尤其要收录用户提问过的问题与踩过的坑（含结论），不要只写"做了什么"

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

## Day28（已完成）

- REST 子资源：`/stocks/{symbol}/risk`（风险标量）、`/stocks/{symbol}/indicators`（指标序列）；指标挂在股票下面，不写“没有主体”的 `/indicators`
- Service 复用：抽取 `_get_stock_data()`（取数 + 空判断），`get_stock_metrics` / `get_stock_risk` / `get_stock_indicators` 共用，不复制三份
- 序列化：先算指标、后对指标列 `dropna()`（MA 预热期 NaN 不能进 JSON），再 `to_dict("records")` 每行一个 dict；`rows` = 有效行数（window=20 → 1436）
- 参数校验：`window: int = Query(20, ge=1)`——类型注解自动转 int + 默认值 + ge 规则，非法输入自动 422
- 契约适配：底层列名 `MA20/RSI/DIF/DEA/MACD` 不动，Service 里 `rename` 成小写（底层稳定，适配在边界）
- 测试：14 个全绿（新增 risk/indicators 404、序列 1436 行、window=5 的 1451 行）
- 提交：`feat: add risk and indicators analysis API`
## Day29（已完成）

- REST 资源创建：`POST /portfolios`（请求体 = 权重 dict，返回 201 + id + weights）；子资源 `GET /portfolios/{id}/performance`
- 持久化：portfolio 表 `weights TEXT` 存 JSON 列；`cursor.lastrowid` 取自增 id；`commit()` 必须在 `close()` 前；建表 `CREATE TABLE IF NOT EXISTS`（Repository 构造时调用）
- 分层：JSON 编解码放 Repository（manager 只碰 SQL）；"查找型"仓库 `df.empty → None`，抛 404 归 Service
- Service 复用：`Portfolio` / `Benchmark` / `PerformanceEvaluator` 全部复用 Day18-19；`date_index()` 按日期对齐是纪律（pandas 按索引相加）
- 校验：空 / 负权重 / 权重和≠1 → `InvalidPortfolioError`(422) fail fast，不裸抛 ValueError
- 测试：19 个全绿（新增创建 201、绩效字段、404、空权重 422、权重和≠1 422）
- 提交：`feat: add portfolio API with persistence`
## Day30（已完成）

- 测试金字塔：单元（Service，mock Repository）→ 集成（Repository，临时 SQLite）→ API（TestClient）；37 个全绿
- mock 纪律：MagicMock 的 return_value / side_effect / 查账断言（assert_called_once / assert_called_once_with）；cast 用在读取侧（实例属性类型由类声明焊死），用返回 Any 的 fixture 收口
- 集成测试：tmp_path 临时库（不碰开发库）；`:memory:` 在单元测试里只是占位
- 覆盖率：pytest-cov + pyproject addopts；核心层 89% → 93%；报告看 TOTAL / Missing
- 真 bug：pd.read_sql 把 sqlite3.Error 重包为 pandas.errors.DatabaseError（不是 sqlite3.Error 子类），Repository 的 except 需同时捕获
- 提交：`fix: catch pandas DatabaseError in repositories` / `test: add unit and integration tests with coverage`
## Day31（已完成）

- 请求日志中间件：新增 `api/middleware.py` 的 `log_requests`（`@app.middleware("http")` 一行挂载），记录 method / path(含查询参数) / status / 耗时；用 `uuid.uuid4().hex[:8]` 生成 request_id
- request_id 链路：`utils/logger.py` 定义 `request_id_var: ContextVar[str]`（default "-"）+ `RequestIdFormatter`（format 时先把当前 id 挂到 record 再 super().format）；中间件/Service/Repository 的日志自动共享同一 id，不用逐层传参
- 踩坑 1（顺序）：`reset(token)` 放 finally 没错，但"请求完成"日志若写在 finally 之后，打出来时 id 已被擦掉 → 显示 "-"；必须把成功日志与 return 放 try 内，finally 在 return 时才执行
- 踩坑 2（caplog）：caplog 用自己的默认 formatter，不经过 RequestIdFormatter，别直接断言 `record.request_id`；正确姿势 = 单测 RequestIdFormatter + `caplog.handler.setFormatter(RequestIdFormatter(...))`
- 分层日志纪律：INFO 查询参数、WARNING 未命中放 Service；ERROR 数据库根因在 Repository 包装前记 `logger.error(..., exc)`——响应 message 不暴露细节，日志留根因
- 敏感信息：中间件只记 method/path/query，不碰 body/header；组合创建只记 id 不记 weights；日志一律 `%s` 占位 + 参数（惰性求值），不用 f-string
- 测试：新增 10 个（中间件日志 6 + formatter 单测 1 + 跨层 request_id 1 + Repository ERROR 2）→ 47 全绿，覆盖率 93%，pyright strict 0 错误
- 提交：`feat: add request logging middleware with request_id tracing`
## 学习路线规划（Day25–Day35）

> 阶段定位：Day1–19 是"我会什么"，Day20–24 是"我怎么把它组织起来"，Day25–35 是"把它做成别人能调用、测试、部署的软件"。
> 原则：**不回头堆金融指标，不做前端**；每个接口/每层改动当天补 pytest + git 提交 + 学习笔记。

主线骨架（所有接口都长这样）：

```
Router → Service → Repository → Database
```

### 逐日安排

- **Day25 Service 层与业务逻辑分离**（已完成）：新增 `services/`（如 `StockService`），把编排逻辑从 `app.py` 挪进 Service；`app.py` 只做"收请求、转参数、回 Response Model"。验收：`GET /stock/600519` 行为不变，配套单测通过。
- **Day26 统一异常与统一响应**（已完成）：扩展 `exceptions.py`（`InvalidDateRangeError` / `DatabaseError` 等），用 FastAPI 异常处理器统一转 JSON（`code` + `message`），去掉接口里散落的 try/except。验收：所有错误响应的结构统一。
- **Day27 RESTful API 设计**（已完成）：学 REST 资源语义；用 `APIRouter` 按资源拆分路由；v1.0 前统一资源命名为复数 `/stocks/{symbol}`（旧路径可先保留兼容）；补 `GET /stocks` 列表。验收：`/docs` 结构清晰、无重复代码。
- **Day28 金融分析 API**（已完成）：把 Day17–19 能力暴露成接口：`GET /stocks/{symbol}/risk`（收益/波动/回撤/Sharpe）、`/stocks/{symbol}/indicators?window=20`（MA/RSI/MACD）。验收：每个新接口都有 pytest 覆盖（14 个全绿）。
- **Day29 Portfolio API（含持久化）**（已完成）：新增 portfolio 表 + `PortfolioRepository` + `PortfolioService`；`POST /portfolios`（请求体 = 权重 dict）、`GET /portfolios/{id}/performance`（组合收益/年化/波动/Sharpe/Benchmark/Excess Return）。验收：组合可入库、可查绩效，接口测试全绿（19 个全绿）。
- **Day30 测试体系系统化**（已完成）：测试金字塔——单元（Service，mock Repository）→ 集成（Repository 用临时数据库）→ API（TestClient）；fixture / monkeypatch / mock；引入覆盖率统计。验收：核心层覆盖率 ≥ 70%（37 全绿，93%）。
- **Day31 日志与可观测性**（已完成）：请求日志中间件（method / path / status / 耗时）；分层日志（INFO 查询参数、WARNING 未命中、ERROR 数据库失败）；不记录敏感信息。验收：一条请求在日志里可完整追踪。
- **Day32 配置与环境管理**：引入 pydantic-settings + `.env`；按 development / testing / production 区分配置；测试用独立临时数据库。验收：改环境变量即可切换环境，代码里无硬编码路径。
- **Day33 Docker 化**：Dockerfile（多阶段构建）+ docker-compose。目标：`docker compose up` → `/docs` 可访问。验收：新环境一条命令启动。
- **Day34 项目文档**：README.md（项目是什么 / 如何运行 / 如何测试）+ ARCHITECTURE.md（分层与数据流图）+ API.md（接口清单与示例）。验收：照着文档能在新环境跑起来。
- **Day35 工程 Review 与 v1.0**：代码走查（重复 / 命名 / 注解 / 异常 / 日志 / 测试 / 配置 / 文档）→ 全量 pytest → 打 tag `v1.0.0`。验收：checklist 全过、Git clean。

### 贯穿原则

- 每个接口/每层改动当天补 pytest + git 提交 + 学习笔记（本地记录不入库）
- 一切为"可调用、可测试、可部署"服务

# AGENTS.md

## 项目简介

金融数据分析学习平台。**v1.0.0 已封版（2026-09-20），项目进入维护模式**：八维度走查 + 修复完成，59 测试全绿、核心层覆盖率 99%、pyright strict 0 错误，版本号 `1.0.0`，tag 已推远端。
**下次开工前的入口先看 [docs/ROADMAP.md](docs/ROADMAP.md)**（复活流程 / 候选项 / 发版流程）；面试讲述素材在 [docs/PROJECT_STORY.md](docs/PROJECT_STORY.md)。维护模式下默认不新增功能。

## 开始任务前必读

- 每次开始任务（包括新对话）前，先读取同目录的 `AGENTS.local.md`——本机路径、笔记位置、协作方式等个人上下文都写在那里（该文件已被 .gitignore 忽略，不会提交）。

## 技术栈

- Python 3.13 + Pandas + Matplotlib + SQLite（标准库 `sqlite3`）
- FastAPI + Uvicorn（API 服务，`.venv` 已安装）
- pytest + httpx + pytest-cov（单元/集成/接口测试与覆盖率，`.venv` 已安装）
- 虚拟环境：`.venv`（用 `.venv\Scripts\python.exe` 运行）
- 包：`finance_analysis`（src 布局，editable install）
- 容器：Docker（本机是 Rancher Desktop + Moby 引擎）；镜像 `finance-analysis:dev`，数据卷 `finance-data`

## 当前结构

```
src/finance_analysis/
├── config.py           # 集中配置：Settings(BaseSettings) + settings 单例（字段默认值可被 .env / FINANCE_* 环境变量覆盖）
├── exceptions.py       # 异常体系（AppError 基类 + 6 个子类，携带 status_code / code）
├── api/                # FastAPI 应用（app.py：include_router + 统一异常处理器 + 旧路径 deprecated；middleware.py：请求日志中间件；routers/stocks.py / portfolios.py：APIRouter；dependencies.py：依赖注入；schemas.py：响应模型）
├── services/           # StockService / PortfolioService（业务编排）
├── models/             # StockData / StockPool / Portfolio（业务对象）
├── repository/         # StockRepository / PortfolioRepository（数据访问层，业务层不直接碰 SQLite）
├── database/           # manager.py（DatabaseManager，连接走 _connect() 上下文管理器）/ loader.py（DatabaseLoader）/ init_db.py（建表+灌库入口）
├── analysis/           # indicators / risk / evaluation / benchmark
├── data/               # download_stock.py
├── utils/              # logger.py（setup_logging）/ utils.py（load_csv / save_csv / save_plot）
└── visualization/      # 绘图（函数内部有 plt.show()，自动化测试需 MPLBACKEND=Agg）

Dockerfile              # 两阶段构建（builder 装依赖 → final 只带 /opt/venv + 源码）
docker-compose.yml      # api 服务：端口映射 / .env / finance-data 数据卷 / healthcheck
.dockerignore           # 构建上下文瘦身（排除 .venv/.git/.env/database/tests 等）
docker/entrypoint.sh    # 容器入口：先 init_db 灌库，再 exec uvicorn

README.md               # 项目是什么 / 怎么跑 / 怎么测 / 怎么配（面向第一次打开仓库的人）
README.en.md            # README 的英文版（双语：两份文件顶部互相跳转）
docs/ARCHITECTURE.md    # 分层架构 / 请求全链路 / 数据库设计 / 关键设计决策
docs/API.md             # 接口清单 / 参数 / 真实响应示例 / 错误码表
docs/ROADMAP.md         # 封版说明 / 复活流程 / 候选项 / 发版流程（维护模式的入口）
docs/PROJECT_STORY.md   # 一页纸项目讲述（面试 / 实习用）

tests/                  # 只放 pytest 真测试（单元 / 集成 / 接口，59 个用例）
examples/               # 早期练习脚本 + 数据库/分析 demo（不被 pytest 收集，不参与 pyright）
pyproject.toml          # version = 1.0.0；pytest-cov / pyright strict 配置
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
- Day32（已完成）：配置与环境管理（引入 pydantic-settings：config.py 改为 `Settings(BaseSettings)` + `settings` 单例；字段 = 类型 + 默认值，可被 .env / `FINANCE_*` 环境变量覆盖；`env_prefix="FINANCE_"` 防裸系统变量劫持；`environment: Literal[development/testing/production]`；收敛全部调用方改走 settings 并删除兼容别名；service 构造改 `db_path=None` + 运行时读 settings（绕开默认参数 import 时求值的陷阱）；新增 .env（gitignored）+ .env.example 模板；测试隔离：`tests/conftest.py` session autouse fixture 用真实 CSV 灌独立临时库并指向 `settings.database_path`，API/日志测试不再碰开发库；`test_config.py` ×4（默认/覆盖/非法环境 fail fast/前缀隔离）；51 全绿、覆盖率 93%、pyright strict 0）
  - 提交：`feat: add pydantic-settings config and isolated test database`
- Day33（已完成）：Docker 化（多阶段 Dockerfile；.dockerignore；entrypoint 先 init_db 灌库再 exec uvicorn；docker-compose 管端口 / .env / finance-data 数据卷 / healthcheck；create_stock_price_table 显式建表修掉"表结构依赖第一个 CSV"的真 bug；pip 缓存挂载 + 清华源把依赖安装从 220s 压到 28s；53 全绿、覆盖率 93%、pyright strict 0）
  - 提交：`fix: create stock_price table explicitly instead of inferring from first CSV` / `build: containerize the API with multi-stage Dockerfile and compose` / `test: lock stock_price schema and init_db idempotency` / `build: cache pip wheels and use a domestic PyPI mirror`
- Day34（已完成）：项目文档（README.md 重写：功能一览 / 技术栈 / 目录结构 / 本地与 Docker 两种跑法 / 测试与类型检查 / 配置表 / 数据来源；docs/ARCHITECTURE.md：分层图 + 每层"该做/不该做" + 一次请求的 10 步全链路 + 表结构 DDL + 10 条关键决策 + 已知边界；docs/API.md：7 个接口的参数表 / 真实响应 / 错误码全表 + 端到端 curl 序列；验收 = 复制到临时目录 + 全新 venv 按文档跑通，53 全绿、覆盖率 93%、pyright strict 0）
  - 提交：`docs: add README, architecture and API documentation`
- Day35（已完成）：工程 Review 与 v1.0（八维度走查发现问题 1 个严重的 + 若干技术债：`tests/` 里 10 个"伪测试"脚本在 pytest 收集阶段就执行、还把数据写进开发库；连接泄漏；空 `main.py`；死代码 `create_unique_index`；`download_stock.py` 残留 print + 硬编码目录；Service/Model 重复组装；model 裸抛 ValueError。修复后 **59 全绿、核心层覆盖率 93% → 99%**、pyright strict 0；版本号 `1.0.0`；**tag `v1.0.0`**）
  - 提交：`fix: isolate test collection from the dev database` / `refactor: use a connection context manager in DatabaseManager` / `refactor: dedupe service metrics and use domain errors in models` / `test: cover database manager and repository error paths` / `chore: drop dead code, replace prints with logging, bump version to 1.0.0` / `docs: update architecture and README for v1.0`

## 约定与注意事项

- 测试在 `tests/test_*.py`：原有为脚本式（`$env:MPLBACKEND='Agg'` 后逐个 `python` 运行）；`test_api.py` 为 pytest 式（`.venv\Scripts\python.exe -m pytest tests/test_api.py -v`）
- 类型检查：项目启用 Pylance/Pyright strict（pyproject `typeCheckingMode = "strict"`）；所有新增代码（含教学示例与测试代码）必须通过 strict 检查，业务代码保持零 `# pyright: ignore`；测试里 mock 用标准写法（如 `typing.cast(Any, MagicMock())`），不要用 `# type: ignore` 绕过
- 日志：程序入口调用一次 `finance_analysis.utils.logger.setup_logging()`
- API 启动：`.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload`（交互文档 http://127.0.0.1:8000/docs）
- 数据库：`database/finance.db` 不入库，新环境用 DatabaseLoader 从 `data/*.csv` 重建
- 容器启动（本机）：`wsl -d rancher-desktop -u root -- sh -c "cd /mnt/d/03_Dev/Develop/Projects/finance-analysis-platform && docker compose up -d --build"`；验证 `curl.exe http://127.0.0.1:8000/docs`。Docker Desktop 的 Windows↔WSL 桥在本机坏了，所以 docker 命令一律进 rancher-desktop 虚拟机执行
- CLI 类型检查：`.venv\Scripts\python.exe -m pyright --pythonpath .venv\Scripts\python.exe src tests`（不加 `--pythonpath` 时 pyright 解析不到三方包，会报成百上千条假错误；`examples/` 是历史遗留目录，不在检查范围）
- 输出产物（`output/`、`*.png`、`*.log`）不入库（.gitignore 已配置）
- README 双语：`README.md`（中文，默认）与 `README.en.md`（英文）是**同一份内容的两版**，改一版必须同步改另一版；两份文件顶部都有语言切换链接
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
## Day32（已完成）

- 配置类化：config.py 从模块级常量改为 `Settings(BaseSettings)` + `settings` 单例；`model_config = SettingsConfigDict(env_file=".env", env_prefix="FINANCE_", extra="ignore")`
- 取值优先级：代码默认值 < .env 文件 < 真实环境变量 < 显式传参；`.env` 相对当前工作目录读取（测试用 chdir 到空目录隔离）
- 防劫持：`env_prefix="FINANCE_"`——裸的 `DATABASE_PATH` 等系统变量无法覆盖配置，用 `test_prefix_protects_against_bare_env_var` 锁死
- 环境：`environment: Literal["development", "testing", "production"]` 记录身份；非法值构造即报错（fail fast）；环境差异由各机器自己的 .env 提供，代码不猜环境
- 收敛调用方：logger / service / model / utils 全部改走 `settings.xxx`，兼容别名删除；`rg` 全仓库确认无裸路径常量
- 默认参数陷阱：`def __init__(db_path=DATABASE_PATH)` 在 import 时把默认值焊死 → 改为 `db_path: str | Path | None = None` + 运行时读 settings（也是测试可注入临时库的前提）
- 测试隔离：`tests/conftest.py` session autouse fixture 用真实 CSV 灌独立临时库并改 `settings.database_path`（yield 后恢复）；API/日志测试从此不碰开发库；DatabaseLoader 覆盖率顺带升到 100%
- 配置测试：`test_config.py` ×4——默认值 / 环境变量覆盖 / 非法环境 ValidationError / env_prefix 隔离裸变量；`clean_env` fixture = 删 FINANCE_* 变量 + chdir 空目录（测试只依赖自己布置的考场）
- 坑：`from pydantic import BaseSettings` 是 pydantic v1 写法，v2 要从 `pydantic_settings` 导入（报错信息会明说 moved）；`Settings(_env_file=None)` 运行时可用但 pyright 按"字段生成 init"不认 → 改用 monkeypatch.chdir 隔离 .env；带 yield 的 fixture 返回注解应为 `Iterator[None]`
- 测试：47 → 51 全绿（+4 配置测试），覆盖率 93%，pyright strict 0 错误
- 提交：`feat: add pydantic-settings config and isolated test database`
## Day33（已完成）

- 镜像 vs 容器：镜像是只读模板（分层，每层是一条构建指令的快照）；容器 = 镜像 + 一层可写层；删容器不动镜像
- Dockerfile：FROM 定基础镜像；单独 COPY requirements.txt（依赖不常变、代码常变 → 让依赖层缓存命中）；两阶段构建 = builder 里装依赖 → final 只带 /opt/venv + 源码
- 实测结论：纯 wheel 项目做多阶段"不会变小"（单阶段 572MB/132MB → 多阶段 589MB/136MB），venv 自带的 pip/setuptools 抵消了收益；多阶段的价值在需要编译工具链的场景
- docker-compose.yml：把「构建 + 端口映射 + env_file + 数据卷 + healthcheck」写成声明式配置，一条 `docker compose up -d --build` 起服务
- 端口映射 `8000:8000` = 宿主机端口:容器端口；容器里的 uvicorn 必须监听 0.0.0.0，绑 127.0.0.1 的话宿主机转发不进去
- 数据卷：`finance-data:/app/database` 把 SQLite 文件放在卷里，`compose down` 再 `up` 数据还在（id=1 的组合重启后仍能查到绩效）
- entrypoint.sh：`#!/bin/sh` 是 shebang（告诉系统用哪个解释器执行这个文件）；`set -e` = 任一条命令失败立刻退出（否则灌库失败还会继续把服务启起来）；先 `python -m finance_analysis.database.init_db` 再 `exec uvicorn ...`——exec 用 uvicorn 替换掉 shell 进程，让 uvicorn 成为 PID 1 才能正确接收 `docker stop` 的信号
- 幂等：entrypoint 每次容器启动都会跑 init_db，所以建表用 `CREATE TABLE IF NOT EXISTS`、写入用 `INSERT OR IGNORE`（靠 UNIQUE(symbol,date) 去重），重复启动既不报错也不灌重复数据
- 真 bug（今天最值钱的一条）：容器灌库报 `sqlite3.OperationalError: table stock_price has no column named outstanding_share`。根因 = 旧逻辑"拿读到的第一个 CSV 建表"，而 `data/000300.csv` 只有 7 列（没有 outstanding_share/turnover），另外三个 CSV 有 9 列，`init_database()` 按文件名排序恰好先读到 000300.csv → 表缺列。本机一直没炸，是因为 `tests/conftest.py` 只灌 600519.csv / 000858.csv（都是 9 列）——典型的"依赖巧合"
- 修复：`DatabaseManager.create_stock_price_table()` 显式声明 11 列 + UNIQUE(symbol,date)，表结构由代码定义、不再由 CSV 顺序决定；回归测试 `tests/test_init_db.py` 锁死「000300 先灌也不缺列」+「init_db 跑两次不重复」
- 依赖层提速：pip 装依赖 220s → 28s，主要靠清华源（`-i https://pypi.tuna.tsinghua.edu.cn/simple`）；再加 `RUN --mount=type=cache,target=/root/.cache/pip` 让 wheel 留在 BuildKit 缓存里、不进镜像层（实测重装时每个包都是 `Using cached`）。注意：加了缓存挂载就不能再带 `--no-cache-dir`，否则 pip 根本不写缓存
- 反面对照：`docker build --network=none` 依然失败——pip 即使有 wheel 缓存也要访问索引才能解析版本，所以"缓存挂载" ≠ "离线构建"
- 坑：容器默认走 UTC，日志时间比本地少 8 小时（要让日志显示本地时间得给容器设 TZ）
- 测试：51 → 53 全绿（+2 个 init_db 回归测试），覆盖率 93%，pyright strict 0 错误
- 提交：`fix: create stock_price table explicitly instead of inferring from first CSV` / `build: containerize the API with multi-stage Dockerfile and compose` / `test: lock stock_price schema and init_db idempotency` / `build: cache pip wheels and use a domestic PyPI mirror`
## Day34（已完成）

- 三份文档的分工（按"读者是谁"分，不按"内容多少"分）：README = 项目是什么 + 5 分钟跑起来（读者：第一次打开仓库的人）；ARCHITECTURE.md = 代码为什么这么分、请求怎么走完全程（读者：要改代码的人）；API.md = 每个接口的参数/返回/错误码（读者：调用方）
- README：功能一览表 + 技术栈 + 目录结构树 + 快速开始（本地 / Docker 两套）+ 测试与类型检查 + 配置环境变量表 + 数据来源与"怎么加新股票" + 文档导航
- ARCHITECTURE.md：mermaid 分层图（Router → Service → Repository → Database，旁挂 Models/Analysis/Schemas/Exceptions/Config）+ 每层职责与纪律表（"该做的事 / 不该做的事"）+ 以 `GET /stocks/600519/indicators?window=20` 为例的 10 步全链路 + 文件级目录树 + 两张表 DDL 与设计取舍 + 10 条关键设计决策 + 日志/测试策略 + 已知边界
- API.md：7 个接口（含废弃的 `/stock/{symbol}`）的方法/路径/参数表/真实响应；错误码总表（`STOCK_NOT_FOUND` / `STOCK_NO_DATA` / `INVALID_DATE_RANGE` / `PORTFOLIO_NOT_FOUND` / `INVALID_PORTFOLIO` / `DATABASE_ERROR` / `VALIDATION_ERROR`）；端到端 curl 序列
- 文档里的所有示例都是**真跑出来的响应**，不是手写的：`/stocks/600519` rows=1455、`window=20` rows=1436、`window=5` rows=1451、权重 0.4/0.3/0.3 的组合收益 0.7196 vs 基准 0.1150（超额 0.6045）
- 验收方法（今天最有价值的一步）：`robocopy` 把仓库复制到临时目录（排除 .venv/.git/database）→ `python -m venv .venv` → `pip install -r requirements.txt`（115s）→ `pip install -e .` → `Copy-Item .env.example .env` → `python -m finance_analysis.database.init_db` → uvicorn → 逐个 curl 与文档对齐。结论：新环境照着 README 确实能跑起来（5820 行 = 4 CSV × 1455，11 列，跑两遍行数不变，`/docs` `/redoc` `/openapi.json` 全 200）
- Docker 路径复验（2026-09-20 补）：按 README 的 Docker 章节逐字跑通 —— `docker compose up -d --build`（层缓存命中，5s）→ `docker compose ps` 显示 `Up (healthy)`（healthcheck 探 `/docs`）→ Windows 侧 `curl.exe http://127.0.0.1:8000/docs` 200、`/stocks/600519` rows=1455（与本地 venv 结果一致）→ 容器内 `docker exec ... python -c` 查卷里数据库：`stock_price` 5820 行 → 新建组合 id=2 → `docker compose down`（删容器 + 网络）→ `up -d` → 再查 `id=2` 绩效仍在（验证 README 的"down 之后 up，数据还在"）→ `docker logs` 显示 `Started server process [1]`（entrypoint 的 `exec` 生效，uvicorn 是 PID 1）。未验：`docker compose down -v`（会真的删数据，需用户点头）
- 真问题（写文档才发现）：本机 `python` 命中的是 **Microsoft Store 别名桩**（`C:\Users\123\AppData\Local\Microsoft\WindowsApps\python.exe`），`python --version` 什么都不打印、`python -m venv .venv` 静默失败；本机真正能用的是 `D:\03_Dev\Develop\Tools\Python3.13\python.exe`（`.venv\pyvenv.cfg` 里的 home 也指向它）。`py -3.13` 也在报 `Unable to create process`（注册表里的 `D:\Python\python.exe` 已不存在）。→ README 第 0 步加"先 `python --version` 确认能打印版本"，并给出完整路径的兜底写法
- 验证脚本的坑：`robocopy /XD database` 会**误伤任意层级的同名目录**，把 `src/finance_analysis/database` 一起排除了 → `ModuleNotFoundError: No module named 'finance_analysis.database'`。按目录名排除时要确认是不是只想排除顶层
- API 文档里 `POST /portfolios` 的 id 是自增值（开发库示例是 38，新环境第一次是 1），已在文档里注明"以接口返回为准"；`GET /stocks` 在灌了 `000300.csv` 的环境会返回 4 个代码（示例已按新环境输出修正）
- 测试：53 全绿，覆盖率 93%，pyright strict 0 错误
- 提交：`docs: add README, architecture and API documentation`

## Day35（已完成）

### 走查的八个维度

重复 / 命名 / 注解 / 异常 / 日志 / 测试 / 配置 / 文档，逐维度过一遍代码 + `rg` 全仓库搜证据，最后用"跑一遍"验证结论。

### 最严重的一条：跑 pytest 会改写开发库

- 现象：`tests/` 里有 10 个文件叫 `test_*.py`，但它们**不是测试**，是模块级脚本（其中 5 个连 `if __name__ == "__main__"` 守卫都没有）——pytest 在**收集阶段 import** 这些文件时，顶层代码当场执行
- 证据：只跑 `pytest --collect-only`（一条测试都不执行），`database/finance.db` 的修改时间从 `16:06:14` 变成 `16:06:42`
- 影响：原来的 `tests/test_db_loader.py` 会把 `300750.csv` 灌进 `settings.database_path`（收集阶段 = 开发库），`tests/test_db_manager.py` 还在开发库里留下一张垃圾表 `test_stock_price`（实测表清单里确实有它）
- 修复：10 个 demo 脚本移到 `examples/` 并改名 `*_demo.py`（`tests/` 只留 pytest 真测试）；`tests/` 的文件名从此不出现"假 test"
- 验证：修完再跑 `pytest` 与 `--collect-only`，开发库 mtime 不变 ✅
- 教训：**文件名 `test_*.py` = 我保证这是测试**；工具脚本放 `tests/` 会被 pytest import 并执行，`testpaths` 只是限制收集范围，挡不住 import

### 其余修复

1. 连接泄漏：`DatabaseManager` 所有操作改走 `_connect()` 上下文管理器（`@contextmanager` + `finally: conn.close()`），异常路径也不漏；测试里的 `ResourceWarning: unclosed database` 消失
2. pyright 抓到的真问题：`@contextmanager` 的返回注解写 `Iterator[x]` 已被弃用 → 改成 `Generator[sqlite3.Connection]`
3. 死代码：`DatabaseManager.create_unique_index()`（UNIQUE 早已写进建表 DDL、无人调用）、根目录空 `main.py`
4. `data/download_stock.py`：4 处 `print` → `logger`；硬编码 `Path(__file__).parents[3]/"data"` → `settings.data_path` + `mkdir(parents=True, exist_ok=True)`
5. 重复：`StockService` 抽出 `_risk_metrics()`，行情接口与风险接口共用同一份四件套组装
6. 异常一致性：`models/portfolio.py` 3 处裸 `ValueError` → `InvalidPortfolioError`（它是 `ValueError` 子类，旧测试不受影响）
7. 可读性：`analysis/evaluation.py` 的括号换行重排；`summary()` 里三次 `calculate_total_return()` 收敛成局部变量
8. 版本：`pyproject.toml` `0.1.0` → `1.0.0`

### 测试账

- 新增 `tests/test_db_manager.py` ×4（`read_dataframe` 往返 / 显式建表 11 列 / `drop_table` 幂等 / 连接失败记日志并抛出）
- `tests/test_stock_repository.py` 补 `get_all_symbols` 的 `DatabaseError` 翻译
- `tests/test_stock_service.py` 补"带了日期区间、但全量也空 → 仍是 `StockNotFoundError`"
- 53 → **59 个**；覆盖率 93% → **99%**（`manager.py` / `stock_repository.py` / `stock_service.py` 三个文件 100%）

### 验收证据

- pytest：59 passed；pyright strict：0 错误
- 本地冒烟：`/stocks`、`/stocks/600519`（rows=1455、latest_close=1377.18）、`/risk`、`indicators`（window=20 → 1436、window=5 → 1451）、2024 区间（242 行）、`/portfolios/1/performance`、404/422 三种错误、旧路径 200 —— **与 Day34 文档里的数字完全一致**（重构没改行为）
- 容器：`docker compose up -d --build` 重建 → `Up (healthy)` → 容器内 `/stocks/600519`、`/portfolios/2/performance` 数字一致（跑的是新代码）
- tag：`v1.0.0`（annotated tag）
- 推送：`git push origin main --follow-tags` → 远端 `3689a7f..c6e21b4`（8 个提交，快进）+ 新 tag `v1.0.0`；本机 push 前要先开代理（`http.proxy` 指向 `127.0.0.1:7890`，代理没开时 git 报 `Failed to connect to github.com port 443`）
- 清理：开发库里由"伪测试"建出来的垃圾表 `test_stock_price` 已 `DROP`（`stock_price` 4365 行、`portfolio` 38 行未受影响）
- 封版归档（2026-09-20）：新增 `docs/ROADMAP.md`（状态 + 复活流程 + 候选项 + 维护检查 + 发版流程）与 `docs/PROJECT_STORY.md`（面试一页纸：三档讲法 / 四个决策 / 四个坑 / 可背数字 / 预判追问）；两份 README 顶部加状态行与文档导航条目；项目转入**维护模式**，默认零投入（每 2 个月有 20 分钟空闲才验活，跳过不算失败）

### 明确不修的技术债（已写进 ARCHITECTURE.md"已知边界"）

- `StockData.from_database()` 与 `StockService._get_stock_data()` 各有一份"空 → 404"逻辑，且 model 自建 `StockRepository` 导致该路径无法被 mock
- `analysis/indicators.py` 的裸 `ValueError`（API 不可达，只有内部调用会触发）
- 组合绩效无日期参数；无鉴权 / 限流 / 分页；SQLite 单实例

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
- **Day32 配置与环境管理**（已完成）：引入 pydantic-settings + `.env`；按 development / testing / production 区分配置；测试用独立临时数据库。验收：改环境变量即可切换环境，代码里无硬编码路径。
- **Day33 Docker 化**（已完成）：Dockerfile（多阶段构建）+ docker-compose。目标：`docker compose up` → `/docs` 可访问。验收：新环境一条命令启动。
- **Day34 项目文档**（已完成）：README.md（项目是什么 / 如何运行 / 如何测试）+ docs/ARCHITECTURE.md（分层与数据流图）+ docs/API.md（接口清单与示例）。验收：照着文档能在新环境跑起来 —— 已在临时目录 + 全新 venv 实测通过。
- **Day35 工程 Review 与 v1.0**（已完成）：代码走查（重复 / 命名 / 注解 / 异常 / 日志 / 测试 / 配置 / 文档）→ 修复 → 全量 pytest（59 全绿、覆盖率 99%）→ 打 tag `v1.0.0`。验收：checklist 全过、Git clean。

### v1.0 之后的候选项（还没排期）

- 数据面：换 PostgreSQL（多实例）、加定时任务把行情增量入库
- 接口面：组合绩效支持日期区间、加 `/health`、分页与限流、鉴权（API Key / OAuth）
- 工程面：pyright 之外再上 ruff（lint + format）、GitHub Actions 跑 pytest/镜像构建、把 `StockData.from_dataframe` 里的取数依赖拆掉
- 业务面：把 AI 财务摘要（原 Roadmap 里的 "AI Financial Report"）接进来

### 贯穿原则

- 每个接口/每层改动当天补 pytest + git 提交 + 学习笔记（本地记录不入库）
- 一切为"可调用、可测试、可部署"服务

# AGENTS.md

## 项目简介

金融数据分析学习平台（暑期导师式每日任务）。当前完成到 **Day24：响应模型与查询参数**（Pydantic 响应模型 + 日期区间筛选）。
下一步 **Day25：待定**。

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
├── exceptions.py       # 业务异常（StockNotFoundError / StockNoDataError）
├── api/                # FastAPI 应用（app.py：GET /stock/{symbol}，schemas.py：StockResponse 响应模型）
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

## 约定与注意事项

- 用户是学生，**中文交流**；每日一课，**先讲清楚再做**；用户自己写核心代码并贴回来核对；避免重复布置已完成的内容
- 测试在 `tests/test_*.py`：原有为脚本式（`$env:MPLBACKEND='Agg'` 后逐个 `python` 运行）；`test_api.py` 为 pytest 式（`.venv\Scripts\python.exe -m pytest tests/test_api.py -v`）
- 日志：程序入口调用一次 `finance_analysis.utils.logger.setup_logging()`
- API 启动：`.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload`（交互文档 http://127.0.0.1:8000/docs）
- 数据库：`database/finance.db` 不入库，新环境用 DatabaseLoader 从 `data/*.csv` 重建
- 输出产物（`output/`、`*.png`、`*.log`）不入库（.gitignore 已配置）
- 学习笔记在 `D:\Notes`（Obsidian）：每日笔记 `Learning_Log\2026-08\`，索引 `Learning_Log\_索引.md`，主题笔记 `Programming\Python\`

## Day24（已完成）

- Pydantic 响应模型：`api/schemas.py` 定义 `StockResponse`（`response_model=` + 自动文档）
- 查询参数：`GET /stock/{symbol}?start=&end=` 日期区间筛选，参数穿透 API → StockData → StockRepository → DatabaseManager（SQL 动态拼接，`start/end` 转 `isoformat()` 绑定）
- 业务异常：`exceptions.py` 的 `StockNotFoundError` / `StockNoDataError`（继承 ValueError）区分两种 404 语义
- 接口测试：`tests/test_api.py`（pytest + TestClient，fixture + parametrize，覆盖正常 / 区间 / 空区间 / 非法日期 / 不存在共 5 个场景）

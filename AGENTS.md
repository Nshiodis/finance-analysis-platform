# AGENTS.md

## 项目简介

金融数据分析学习平台（暑期导师式每日任务）。当前完成到 **Day23：FastAPI 服务化**（`GET /stock/600519` 返回 JSON 指标）。
下一步 **Day24：响应模型与查询参数**（Pydantic BaseModel 定义返回结构，支持日期区间筛选）。

## 技术栈

- Python 3.13 + Pandas + Matplotlib + SQLite（标准库 `sqlite3`）
- FastAPI + Uvicorn（API 服务，`.venv` 已安装）
- 虚拟环境：`.venv`（用 `.venv\Scripts\python.exe` 运行）
- 包：`finance_analysis`（src 布局，editable install）

## 当前结构

```
src/finance_analysis/
├── config.py           # 集中配置：PROJECT_ROOT / DATA_PATH / OUTPUT_PATH / DATABASE_PATH / LOG_PATH / LOG_LEVEL
├── api/                # FastAPI 应用（app.py：GET /stock/{symbol} 返回 JSON 指标，404 错误处理）
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

## 约定与注意事项

- 用户是学生，**中文交流**；每日一课，**先讲清楚再做**；用户自己写核心代码并贴回来核对；避免重复布置已完成的内容
- 测试在 `tests/test_*.py`，是脚本式（非 pytest 断言式）：`$env:MPLBACKEND='Agg'` 后逐个 `python` 运行
- 日志：程序入口调用一次 `finance_analysis.utils.logger.setup_logging()`
- API 启动：`.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload`（交互文档 http://127.0.0.1:8000/docs）
- 数据库：`database/finance.db` 不入库，新环境用 DatabaseLoader 从 `data/*.csv` 重建
- 输出产物（`output/`、`*.png`、`*.log`）不入库（.gitignore 已配置）
- 学习笔记在 `D:\Notes`（Obsidian）：每日笔记 `Learning_Log\2026-08\`，索引 `Learning_Log\_索引.md`，主题笔记 `Programming\Python\`

## Day24 计划

- Pydantic 响应模型：用 BaseModel 定义 `/stock/{symbol}` 的返回结构（字段校验 + 自动文档）
- 查询参数：支持可选日期区间（如 `?start=2022-01-01&end=2023-12-31`）
- 可选：FastAPI TestClient 接口测试（tests/test_api.py，脚本式）

# 接口手册（API）

本文是调用方手册：**有哪些接口、参数怎么传、返回什么、报错了怎么排查**。
写代码改动看 [ARCHITECTURE.md](ARCHITECTURE.md)，跑起来看 [README](../README.md)。

## 启动服务

```powershell
.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload
```

| 地址 | 说明 |
| --- | --- |
| `http://127.0.0.1:8000` | Base URL |
| `http://127.0.0.1:8000/docs` | Swagger UI（可以直接点着试） |
| `http://127.0.0.1:8000/redoc` | ReDoc 版文档 |
| `http://127.0.0.1:8000/openapi.json` | OpenAPI 契约，可导入 Postman / 生成客户端 |

## 通用约定

- 请求与响应都是 **JSON（UTF-8）**
- 日期参数格式 `YYYY-MM-DD`（如 `2024-01-01`），可只传 `start` 或只传 `end`
- 收益率、波动率等比率都用**小数**表示：`0.2187` = +21.87%
- 错误响应统一为：

  ```json
  {"code": "STOCK_NOT_FOUND", "message": "股票 999999 不存在"}
  ```

  `code` 给程序判断，`message` 给人看
- Windows PowerShell 里请用 `curl.exe`（`curl` 是 `Invoke-WebRequest` 的别名，参数不兼容）

## 接口总表

| 方法 | 路径 | 说明 | 状态码 |
| --- | --- | --- | --- |
| GET | `/stocks` | 股票代码列表 | 200 |
| GET | `/stocks/{symbol}` | 单只股票的行情指标 | 200 / 404 / 422 |
| GET | `/stocks/{symbol}/risk` | 单只股票的风险指标 | 200 / 404 / 422 |
| GET | `/stocks/{symbol}/indicators` | 技术指标序列（MA / RSI / MACD） | 200 / 404 / 422 |
| POST | `/portfolios` | 创建投资组合 | 201 / 422 |
| GET | `/portfolios/{portfolio_id}/performance` | 查询组合绩效 | 200 / 404 |
| GET | `/stock/{symbol}` | **已废弃**，等价于 `/stocks/{symbol}` | 200 / 404 / 422 |

---

## 1. `GET /stocks` —— 股票代码列表

返回库里所有股票代码（升序），常用于「我该查哪只」。

```powershell
curl.exe http://127.0.0.1:8000/stocks
```

```json
{"symbols": ["000300", "000858", "300750", "600519"]}
```

> 列表就是库里的实际内容（按代码升序）：`init_db` 会把 `data/` 下的 CSV 全灌进去，
> 所以典型的新环境是上面 4 个；如果你的库没灌 `000300.csv`，就会少这一项。

## 2. `GET /stocks/{symbol}` —— 行情指标

### 参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `symbol` | path | string | 是 | 股票代码，如 `600519` |
| `start` | query | date | 否 | 起始日期（含） |
| `end` | query | date | 否 | 结束日期（含） |

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `symbol` | string | 股票代码 |
| `rows` | int | 参与计算的交易日数 |
| `latest_close` | float | 区间内最后一个收盘价 |
| `total_return` | float | 区间累计收益率 |
| `volatility` | float | 年化波动率（日收益标准差 × √252） |
| `sharpe` | float | 夏普比率（年化无风险利率按 1.5%） |
| `max_drawdown` | float | 最大回撤（负数） |

### 示例

```powershell
# 全历史
curl.exe http://127.0.0.1:8000/stocks/600519

# 指定区间
curl.exe "http://127.0.0.1:8000/stocks/600519?start=2024-01-01&end=2024-12-31"
```

```json
{"symbol": "600519", "rows": 1455, "latest_close": 1377.18, "total_return": 0.21874336283185802, "volatility": 0.2778720090780447, "sharpe": 0.20777778370771738, "max_drawdown": -0.5151864667435593}
```

```json
{"symbol": "600519", "rows": 242, "latest_close": 1524.0, "total_return": -0.09555432905442751, "volatility": 0.2763472551365687, "sharpe": -0.298644499639681, "max_drawdown": -0.28757062146892653}
```

### 可能的错误

| 场景 | 状态码 | code |
| --- | --- | --- |
| 股票不存在 | 404 | `STOCK_NOT_FOUND` |
| 股票存在但区间内没有数据 | 404 | `STOCK_NO_DATA` |
| `start` 晚于 `end` | 422 | `INVALID_DATE_RANGE` |
| 日期格式不合法 | 422 | `VALIDATION_ERROR` |

```powershell
curl.exe -s -w "`nHTTP %{http_code}" http://127.0.0.1:8000/stocks/999999
# {"code":"STOCK_NOT_FOUND","message":"股票 999999 不存在"}
# HTTP 404

curl.exe -s -w "`nHTTP %{http_code}" "http://127.0.0.1:8000/stocks/600519?start=2024-12-31&end=2024-01-01"
# {"code":"INVALID_DATE_RANGE","message":"开始日期不能晚于结束日期"}
# HTTP 422
```

## 3. `GET /stocks/{symbol}/risk` —— 风险指标

参数与 `GET /stocks/{symbol}` 完全一致，只是不返回 `latest_close`（风险视角不需要当前价）。

```powershell
curl.exe http://127.0.0.1:8000/stocks/600519/risk
```

```json
{"symbol": "600519", "rows": 1455, "total_return": 0.21874336283185802, "volatility": 0.2778720090780447, "sharpe": 0.20777778370771738, "max_drawdown": -0.5151864667435593}
```

## 4. `GET /stocks/{symbol}/indicators` —— 技术指标序列

### 参数

| 参数 | 位置 | 类型 | 必填 | 默认 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `symbol` | path | string | 是 | — | 股票代码 |
| `window` | query | int ≥ 1 | 否 | 20 | **同时**作用于 MA 和 RSI |
| `start` / `end` | query | date | 否 | — | 日期区间 |

MACD 参数固定：快线 12、慢线 26、信号线 9。

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `symbol` | string | 股票代码 |
| `window` | int | 本次使用的窗口 |
| `rows` | int | 有效序列长度 |
| `series` | array | 每个元素一天：`date` / `ma` / `rsi` / `dif` / `dea` / `macd` |

> `series` 只有**有效行**：开头的 `window - 1` 天 MA 为 NaN，已在 Service 里 `dropna()` 丢掉。
> 所以全历史 1455 行、`window=20` 时 `rows = 1436`；`window=5` 时为 1451。

### 示例

```powershell
curl.exe "http://127.0.0.1:8000/stocks/600519/indicators?window=20"
```

```json
{
  "symbol": "600519",
  "window": 20,
  "rows": 1436,
  "series": [
    {"date": "2020-02-06", "ma": 1085.0125, "rsi": 15.36536080273892, "dif": -18.952202964765092, "dea": -15.038501534453289, "macd": -3.9137014303118036},
    {"date": "2020-02-07", "ma": 1082.3125, "rsi": 16.100821325861588, "dif": -16.957064497527654, "dea": -15.422214127068163, "macd": -1.5348503704594911},
    {"date": "2020-02-10", "ma": 1081.709, "rsi": 15.825490207987627, "dif": -15.959311402141793, "dea": -15.529633582082889, "macd": -0.4296778200589042}
  ]
}
```

（真实响应里 `series` 有 1436 个元素，这里只截前 3 个。）

### 参数校验示例

```powershell
curl.exe -s -w "`nHTTP %{http_code}" "http://127.0.0.1:8000/stocks/600519/indicators?window=0"
# {"code":"VALIDATION_ERROR","message":"Input should be greater than or equal to 1"}

curl.exe -s -w "`nHTTP %{http_code}" "http://127.0.0.1:8000/stocks/600519/indicators?window=abc"
# {"code":"VALIDATION_ERROR","message":"Input should be a valid integer, unable to parse string as an integer"}
```

## 5. `POST /portfolios` —— 创建投资组合

### 请求体

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `weights` | object | `{股票代码: 权重}`，权重为小数 |

校验规则（不满足 → 422 `INVALID_PORTFOLIO`）：

1. 不能为空
2. 不能有负数
3. 权重和必须为 1（浮点比较用 `np.isclose`，允许 `0.1 + 0.2` 这类误差）

### 示例

```powershell
curl.exe -X POST http://127.0.0.1:8000/portfolios -H "Content-Type: application/json" -d "{\"weights\":{\"600519\":0.4,\"000858\":0.3,\"300750\":0.3}}"
```

```json
{"id": 38, "weights": {"000858": 0.3, "300750": 0.3, "600519": 0.4}}
```

返回 201，`id` 是数据库自增值 —— 记下它，下一步要用。
（示例里的 `38` 是这个开发库的历史计数，新环境第一次创建会是 `1`，以接口返回为准。）

### 错误示例

```powershell
# 权重和不是 1
curl.exe -s -X POST http://127.0.0.1:8000/portfolios -H "Content-Type: application/json" -d "{\"weights\":{\"600519\":0.5,\"000858\":0.3}}"
# {"code":"INVALID_PORTFOLIO","message":"权重和必须为 1"}
```

## 6. `GET /portfolios/{portfolio_id}/performance` —— 组合绩效

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `portfolio_id` | path | int | 是 | 创建时返回的 id |

### 响应字段

| 字段 | 说明 |
| --- | --- |
| `id` | 组合 id |
| `portfolio_total_return` | 组合累计收益率（各股票按日期对齐后加权） |
| `annualized_return` | 年化收益率 |
| `volatility` | 年化波动率 |
| `sharpe` | 夏普比率 |
| `benchmark_total_return` | 基准（沪深300，`data/000300.csv`）累计收益率 |
| `excess_total_return` | 超额收益 = 组合 − 基准 |

### 示例

```powershell
# 38 换成你创建时返回的 id
curl.exe http://127.0.0.1:8000/portfolios/38/performance
```

```json
{"id": 38, "portfolio_total_return": 0.7195957021024462, "annualized_return": 0.09843629133604948, "volatility": 0.2971962061143135, "sharpe": 0.4143306056510711, "benchmark_total_return": 0.1150463364352754, "excess_total_return": 0.6045493656671708}
```

参数写错时：

```powershell
curl.exe -s -w "`nHTTP %{http_code}" http://127.0.0.1:8000/portfolios/999/performance
# {"code":"PORTFOLIO_NOT_FOUND","message":"组合 999 不存在"}
# HTTP 404
```

> 组合绩效用的是全历史区间，不支持 `start` / `end`；组合里任一股票在库里查不到数据，会直接抛 404。

## 7. `GET /stock/{symbol}` —— 旧路径（已废弃）

Day23 的第一版路径，保留是为了向后兼容，行为与 `/stocks/{symbol}` 一致，在 `/docs` 里标记为 deprecated。
新代码请用 `/stocks/{symbol}`。

---

## 错误码总表

| code | HTTP | 触发场景 | 由谁抛出 |
| --- | --- | --- | --- |
| `STOCK_NOT_FOUND` | 404 | 股票代码在库里完全没有数据 | `StockService` |
| `STOCK_NO_DATA` | 404 | 股票存在，但指定日期区间内无数据 | `StockService` |
| `INVALID_DATE_RANGE` | 422 | `start > end` | `StockService` |
| `PORTFOLIO_NOT_FOUND` | 404 | 组合 id 不存在 | `PortfolioService` |
| `INVALID_PORTFOLIO` | 422 | 权重为空 / 有负数 / 和不等于 1 | `PortfolioService` |
| `DATABASE_ERROR` | 500 | SQLite 查询或写入失败（根因只进日志） | `Repository` |
| `VALIDATION_ERROR` | 422 | 参数类型、格式或范围不满足声明式校验 | FastAPI / 请求校验处理器 |

## 端到端示例

```powershell
# 0. 服务先起来
.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app

# 1. 看有哪些股票
curl.exe http://127.0.0.1:8000/stocks

# 2. 看茅台全历史 + 2024 年表现
curl.exe http://127.0.0.1:8000/stocks/600519
curl.exe "http://127.0.0.1:8000/stocks/600519?start=2024-01-01&end=2024-12-31"

# 3. 看 MACD/RSI 序列
curl.exe "http://127.0.0.1:8000/stocks/600519/indicators?window=20"

# 4. 建一个三只股票的组合
curl.exe -X POST http://127.0.0.1:8000/portfolios -H "Content-Type: application/json" -d "{\"weights\":{\"600519\":0.4,\"000858\":0.3,\"300750\":0.3}}"

# 5. 用返回的 id 查绩效（示例里是 38）
curl.exe http://127.0.0.1:8000/portfolios/38/performance
```

对应 `src/finance_analysis/` 里的实现位置：路由 `api/routers/`，业务 `services/`，取数 `repository/`，计算 `analysis/`。

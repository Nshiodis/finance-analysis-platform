# 路线图与复活指南（ROADMAP）

> **状态：v1.0.0 已封版（2026-09-20），项目进入维护模式。**
> 这份文件有两个用途：① 把"以后想做什么"从脑子里挪到纸上，好结账；② 未来（实习 / 复试 / 有空时）回来时，照着它能重新上手，不用重新摸索。

## 一、复活流程（回来时照着做，约 15 分钟）

```powershell
# 1. 取代码（远端已同步 v1.0.0）
git clone https://github.com/Nshiodis/finance-analysis-platform.git
cd finance-analysis-platform
git describe --tags            # 应输出 v1.0.0

# 2. 装环境（注意：本机 PATH 里的 python 是 Microsoft Store 别名桩，要用真解释器）
python --version               # 必须能打印版本；不行就用完整路径
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
Copy-Item .env.example .env

# 3. 灌库（幂等，可重复执行）+ 起服务
.venv\Scripts\python.exe -m finance_analysis.database.init_db
.venv\Scripts\python.exe -m uvicorn finance_analysis.api.app:app --reload

# 4. 自检（健康的话应该 59 passed / 覆盖率 99% / pyright 0）
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m pyright --pythonpath .venv\Scripts\python.exe src tests

# 5. 容器（本机要进 rancher-desktop 虚拟机跑）
wsl -d rancher-desktop -u root -- sh -c "cd /mnt/d/03_Dev/Develop/Projects/finance-analysis-platform && docker compose up -d --build"
curl.exe http://127.0.0.1:8000/docs
```

期望结果：`GET /stocks/600519` 返回 `rows=1455`、`latest_close=1377.18`；`indicators?window=20` 返回 `rows=1436`。数字对得上说明数据和环境都没问题。

## 二、简历 / 面试素材在哪

| 素材 | 位置 |
| --- | --- |
| 一页纸项目讲述（面试用） | [PROJECT_STORY.md](PROJECT_STORY.md) |
| 架构、请求全链路、关键决策 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 接口清单与真实响应 | [API.md](API.md) |
| 分层实现逐层拆解（6 篇笔记） | Obsidian `04_Projects/Finance_Analysis/Review/md格式/` |
| 每日过程与踩坑记录（Day20–Day35） | Obsidian `04_Projects/Finance_Analysis/Logs/` |

## 三、候选项（复试后再看，现在不做）

按"性价比"排序，每条都标了大概工作量。判断标准：**能不能在面试里讲出一个取舍**，讲不出来的就不值得做。

| 候选项 | 价值 | 工作量 |
| --- | --- | --- |
| 组合绩效支持日期区间（`?start=&end=`） | 接口完整性；顺便练"参数穿透到 SQL" | 0.5 天 |
| `GET /health` + 更细的 readiness 探针 | 运维常识；面试常问"你怎么知道服务活着" | 0.5 天 |
| ruff（lint + format）接进 pytest 流程 | 工程质量；替掉"靠人肉走查" | 0.5 天 |
| GitHub Actions：pytest + 镜像构建 | CI 入门；README 能挂状态徽章 | 1 天 |
| AI 财务摘要（把指标喂给大模型，生成周报） | 正好接"金融 + AI"的面试题；也是原 Roadmap 里唯一没做的块 | 2–3 天 |
| 换 PostgreSQL + 连接池 | 多实例部署的必经之路 | 2 天 |
| 鉴权（API Key）+ 限流 + 分页 | 对外提供服务的门槛 | 2 天 |
| 定时任务增量入库（替代手动 init_db） | 数据新鲜度；涉及调度与幂等 | 2 天 |

**明确不建议做的**：给现有接口堆更多金融指标（MACD 已经够了，再加 BOLL/KDJ 只是重复劳动，面试讲不出新东西）。

## 四、维护检查（每 2 个月一次，有 20 分钟空闲才做，**跳过不算失败**）

目标只有一个：确认项目还活着，别等回来时发现跑不起来。

```powershell
.venv\Scripts\python.exe -m pytest -q      # 期望 59 passed
git tag -l                                  # 期望看到 v1.0.0
git status -sb                              # 期望与 origin/main 同步
```

坏了才修，不坏不碰。**不要为了刷 commit 而提交。**

## 五、发下一个版本的流程（v1.1.0 示例）

```powershell
# 1. 改代码 + 补测试
# 2. 全量验收
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m pyright --pythonpath .venv\Scripts\python.exe src tests

# 3. 版本号：加功能用 MINOR，修 bug 用 PATCH（语义化版本）
#    pyproject.toml: version = "1.1.0"

# 4. 提交 + 打注释 tag + 推送（--follow-tags 会带上注释 tag）
git add .; git commit -m "feat: ..."
git tag -a v1.1.0 -m "v1.1.0 - 这次加了什么"
git push origin main --follow-tags
```

发版前三个前提：测试全绿、类型检查 0、`git status` 干净。本机 push 前记得开代理（`127.0.0.1:7890`）。

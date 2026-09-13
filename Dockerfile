# ---------- 阶段 1：builder（负责装依赖）----------
FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .

# --mount=type=cache：BuildKit 缓存挂载，pip 下载的 wheel 存缓存里、不进镜像层，
# 依赖变动重装时直接复用已下载的包（所以这里不能再加 --no-cache-dir，加了 pip 就不写缓存）
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt


# ---------- 阶段 2：final（只放运行时需要的东西）----------
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

COPY . .

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

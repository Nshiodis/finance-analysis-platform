import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from finance_analysis.utils.logger import request_id_var


logger = logging.getLogger(__name__)


async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """记录请求日志"""
    request_id = uuid.uuid4().hex[:8]
    token = request_id_var.set(request_id)
    path = request.url.path
    if request.url.query:
        path = f"{path}?{request.url.query}"

    logger.info("请求开始 %s %s", request.method, path)
    start = time.perf_counter()

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info("请求完成 %s %s -> %s 耗时 %.1f ms", request.method, path, response.status_code, duration_ms)
        return response
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error("请求异常 %s %s -> 500 耗时 %.1f ms", request.method, path, duration_ms)
        raise
    finally:
        request_id_var.reset(token)


from datetime import date
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from finance_analysis.exceptions import AppError
from finance_analysis.utils.logger import setup_logging
from finance_analysis.api.schemas import StockResponse
from finance_analysis.services.stock_service import StockService


setup_logging()

app = FastAPI()

service = StockService()

@app.exception_handler(AppError)
async def handle_app_error(request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": str(exc)}
    )

@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={"code": "VALIDATION_ERROR", "message": exc.errors()[0]["msg"]}
    )


@app.get("/stock/{symbol}", response_model=StockResponse)
def get_stock(symbol: str, start: date | None = None, end: date | None = None):
    """获取股票数据"""
    return service.get_stock_metrics(symbol, start, end)

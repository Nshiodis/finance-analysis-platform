from datetime import date

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from finance_analysis.api.dependencies import get_stock_service
from finance_analysis.api.routers import stocks
from finance_analysis.api.schemas import StockResponse
from finance_analysis.exceptions import AppError
from finance_analysis.services.stock_service import StockService
from finance_analysis.utils.logger import setup_logging


setup_logging()

app = FastAPI()


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


app.include_router(stocks.router)


@app.get("/stock/{symbol}", response_model=StockResponse, deprecated=True)
def get_stock_legacy(
    symbol: str,
    start: date | None = None,
    end: date | None = None,
    service: StockService = Depends(get_stock_service)
):
    """已废弃：请改用 GET /stocks/{symbol}"""
    return service.get_stock_metrics(symbol, start, end)

class AppError(ValueError):
    """业务异常基类：处理器通过 status_code / code 生成统一响应"""
    status_code = 500
    code = "INTERNAL_ERROR"


class StockNotFoundError(AppError):
    """股票不存在"""
    status_code = 404
    code = "STOCK_NOT_FOUND"


class StockNoDataError(AppError):
    """股票指定区间数据为空"""
    status_code = 404
    code = "STOCK_NO_DATA"


class InvalidDateRangeError(AppError):
    """日期范围无效"""
    status_code = 422
    code = "INVALID_DATE_RANGE"


class DatabaseError(AppError):
    """数据库错误"""
    status_code = 500
    code = "DATABASE_ERROR"
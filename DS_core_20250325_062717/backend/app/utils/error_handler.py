from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import logging
import socket
import traceback

logger = logging.getLogger(__name__)

async def connection_error_handler(request: Request, exc: ConnectionError):
    logger.error(f"连接错误: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"code": 503, "message": "服务连接暂时不可用，请稍后重试", "data": None}
    )

async def socket_error_handler(request: Request, exc: socket.error):
    logger.error(f"Socket错误: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"code": 503, "message": "网络连接异常，请稍后重试", "data": None}
    )

async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"值错误: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": 400, "message": f"请求参数错误: {str(exc)}", "data": None}
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )

def setup_exception_handlers(app: FastAPI):
    """设置FastAPI应用的全局异常处理器"""
    app.add_exception_handler(ConnectionError, connection_error_handler)
    app.add_exception_handler(ConnectionResetError, connection_error_handler)
    app.add_exception_handler(socket.error, socket_error_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler) 
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging
import traceback
from ..utils.error_handler import (
    connection_error_handler,
    socket_error_handler,
    value_error_handler,
    generic_exception_handler
)

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """配置应用程序的异常处理程序"""
    
    # 连接错误处理
    @app.exception_handler(ConnectionError)
    async def handle_connection_error(request: Request, exc: ConnectionError):
        return connection_error_handler(request, exc)
    
    # 套接字错误处理
    @app.exception_handler(ConnectionResetError)
    async def handle_connection_reset_error(request: Request, exc: ConnectionResetError):
        return socket_error_handler(request, exc)
    
    # 值错误处理
    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError):
        return value_error_handler(request, exc)
    
    # 通用异常处理
    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception):
        return generic_exception_handler(request, exc)
    
    logger.info("异常处理程序已配置")
    return app 
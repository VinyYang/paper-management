import os
import sys
import logging
import argparse
import uvicorn

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保可以导入backend模块
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
sys.path.append(current_dir)
sys.path.append(backend_dir)

try:
    # 导入database模块
    from backend.app.database import init_db
except ImportError as e:
    logger.error(f"导入错误: {e}")
    sys.exit(1)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="启动文献管理系统API服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务器绑定的主机地址")
    parser.add_argument("--port", type=int, default=8001, help="服务器绑定的端口")
    parser.add_argument("--reload", action="store_true", help="是否启用自动重载")
    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()
    
    # 初始化数据库
    try:
        logger.info("初始化数据库...")
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)
        
    # 启动 FastAPI 应用
    print(f"启动服务器，访问地址: http://{args.host}:{args.port}")
    print(f"API 文档地址: http://{args.host}:{args.port}/docs")
    
    # 使用正确的模块路径
    uvicorn.run(
        "backend.app.main:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload,
        log_level="info"
    ) 
import uvicorn
import sys
import os
import logging
import argparse

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

# 导入数据库初始化函数
from app.database import init_db

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="启动文献管理系统API服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务器绑定的主机地址")
    parser.add_argument("--port", type=int, default=8003, help="服务器绑定的端口")
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
        
    # 设置环境变量
    if args.host == "0.0.0.0":
        os.environ["BASE_URL"] = f"http://{args.host}:{args.port}"
    else:
        os.environ["BASE_URL"] = f"http://{args.host}:{args.port}"
    
    # 启动 FastAPI 应用
    print(f"启动服务器，访问地址: http://{args.host}:{args.port}")
    print(f"API 文档地址: http://{args.host}:{args.port}/docs")
    uvicorn.run(
        "app.main:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload,
        log_level="info"
    ) 
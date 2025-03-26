"""
显式初始化数据库，创建所有表和初始数据
"""
import logging
import sys
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

# 导入必要的组件
from app.database import init_db, SessionLocal, engine
from app.models import User, UserRole, Concept
from sqlalchemy import text, inspect

def create_minimal_data():
    """创建最小化的初始数据"""
    db = SessionLocal()
    try:
        # 检查表是否已创建
        inspector = inspect(engine)
        
        # 只有当users表存在时才创建管理员用户
        if inspector.has_table("users"):
            logger.info("检测到users表存在，尝试创建管理员用户")
            # 检查是否存在管理员用户
            admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if not admin_exists:
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                    role=UserRole.ADMIN
                )
                db.add(admin_user)
                db.commit()
                logger.info("管理员用户已创建")
            else:
                logger.info("管理员用户已存在，跳过创建")
        else:
            logger.warning("users表不存在，跳过创建管理员用户")
        
        logger.info("初始数据创建完成")
    except Exception as e:
        db.rollback()
        logger.error(f"创建初始数据时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始初始化数据库...")
    try:
        # 初始化数据库结构
        init_db()
        logger.info("数据库初始化成功")
        
        # 创建必要的初始数据
        create_minimal_data()
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}") 
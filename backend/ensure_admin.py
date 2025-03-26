import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 密码处理
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def ensure_admin_exists():
    """确保管理员用户存在"""
    try:
        # 连接数据库
        engine = create_engine(f"sqlite:///./app.db")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 检查admin用户是否存在
        result = db.execute(text("SELECT id FROM users WHERE username = 'admin'")).fetchone()
        
        if not result:
            logger.info("管理员用户不存在，创建中...")
            # 创建密码哈希
            hashed_password = get_password_hash("password")
            
            # 创建admin用户
            db.execute(
                text("""
                INSERT INTO users (username, email, hashed_password, role, is_active, created_at)
                VALUES (:username, :email, :hashed_password, :role, :is_active, CURRENT_TIMESTAMP)
                """),
                {
                    "username": "admin",
                    "email": "admin@example.com",
                    "hashed_password": hashed_password,
                    "role": "admin",
                    "is_active": True
                }
            )
            db.commit()
            logger.info("管理员用户创建成功")
        else:
            logger.info("管理员用户已存在")
            
            # 重置密码
            hashed_password = get_password_hash("password")
            db.execute(
                text("""
                UPDATE users 
                SET hashed_password = :hashed_password 
                WHERE username = 'admin'
                """),
                {"hashed_password": hashed_password}
            )
            db.commit()
            logger.info("管理员密码已重置")
            
    except Exception as e:
        logger.error(f"确保管理员用户存在时出错: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始确保管理员用户存在...")
    ensure_admin_exists()
    logger.info("完成") 
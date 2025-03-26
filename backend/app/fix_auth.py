import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保可以导入backend模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)
sys.path.append(root_dir)

# 导入所需模块
try:
    from backend.app.models import User, UserRole
    from backend.app.database import SessionLocal, engine
except ImportError as e:
    logger.error(f"导入错误: {e}")
    sys.exit(1)

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_admin_password():
    """重置管理员密码"""
    db = SessionLocal()
    try:
        # 查找管理员用户
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            # 不存在则创建管理员
            logger.info("未找到管理员用户，创建新管理员用户")
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("password"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
        else:
            # 重置管理员密码
            logger.info(f"重置管理员 {admin.username} 的密码")
            admin.hashed_password = pwd_context.hash("password")
            admin.is_active = True
        
        db.commit()
        logger.info("管理员密码已重置为: password")
    except Exception as e:
        db.rollback()
        logger.error(f"重置管理员密码时出错: {e}")
    finally:
        db.close()

def list_all_users():
    """列出所有用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"系统中共有 {len(users)} 个用户:")
        for user in users:
            logger.info(f"ID: {user.id}, 用户名: {user.username}, 角色: {user.role}, 激活状态: {user.is_active}")
    except Exception as e:
        logger.error(f"列出用户时出错: {e}")
    finally:
        db.close()

def fix_user_fields():
    """修复用户字段问题"""
    inspector = inspect(engine)
    if not inspector.has_table('users'):
        logger.error("users表不存在")
        return
    
    # 检查必要的字段
    columns = {col['name'] for col in inspector.get_columns('users')}
    missing_fields = []
    
    if 'hashed_password' not in columns:
        missing_fields.append('hashed_password')
    
    if 'is_active' not in columns:
        missing_fields.append('is_active')
    
    try:
        with engine.connect() as conn:
            # 修复缺失字段
            for field in missing_fields:
                if field == 'hashed_password' and 'password' in columns:
                    # 重命名 password -> hashed_password
                    logger.info("重命名 password 字段为 hashed_password...")
                    # SQLite 需要创建新表并复制数据
                    conn.execute(text("""
                        ALTER TABLE users RENAME TO users_old;
                    """))
                    # 获取所有字段
                    columns_str = ", ".join([
                        col['name'] if col['name'] != 'password' else 'password as hashed_password' 
                        for col in inspector.get_columns('users_old')
                    ])
                    # 创建新表
                    conn.execute(text(f"""
                        CREATE TABLE users AS 
                        SELECT {columns_str} FROM users_old;
                    """))
                    # 删除旧表
                    conn.execute(text("DROP TABLE users_old;"))
                    logger.info("password 字段重命名完成")
                
                elif field == 'is_active':
                    logger.info("添加 is_active 字段...")
                    conn.execute(text("""
                        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;
                    """))
                    logger.info("is_active 字段添加完成")
            
            conn.commit()
            logger.info("用户表字段修复完成")
    except Exception as e:
        logger.error(f"修复用户字段时出错: {e}")

def main():
    """主函数"""
    # 修复用户字段
    fix_user_fields()
    
    # 重置管理员密码
    reset_admin_password()
    
    # 列出所有用户
    list_all_users()
    
    logger.info("用户认证修复操作完成")

if __name__ == "__main__":
    main() 
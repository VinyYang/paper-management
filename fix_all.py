import os
import sys
import logging
import argparse
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import datetime
import shutil

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保可以导入backend模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 环境配置
ENV_FILE = os.path.join(current_dir, '.env')
if not os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'w') as f:
        f.write("""DATABASE_URL=sqlite:///app.db
SQLALCHEMY_DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-goes-here-make-it-very-secure-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIRECTORY=uploads""")
    logger.info(f"已创建环境配置文件 {ENV_FILE}")

# 导入所需模块
try:
    from backend.app.config import settings
    database_url = settings.DATABASE_URL
except ImportError:
    logger.warning("无法导入settings，使用默认数据库URL")
    database_url = "sqlite:///app.db"

# 创建数据库引擎
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False}
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 密码处理工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def clean_duplicate_files():
    """清理重复文件"""
    logger.info("开始清理重复文件...")
    
    # 需要保留的核心文件
    core_files = {
        'run.py', '.env', 'README.md', 'requirements.txt', 
        'app.db', 'fix_all.py'
    }
    
    # 需要保留的核心目录
    core_dirs = {
        'backend', 'frontend', 'uploads', 'venv'
    }
    
    # 清理根目录中的其他文件
    for item in os.listdir(current_dir):
        if os.path.isfile(os.path.join(current_dir, item)):
            if item not in core_files and not item.endswith('.md'):
                if item.startswith('fix_') and item != 'fix_all.py':
                    try:
                        os.remove(os.path.join(current_dir, item))
                        logger.info(f"已删除冗余文件: {item}")
                    except Exception as e:
                        logger.error(f"删除文件 {item} 时出错: {e}")
    
    # 清理backend目录中的冗余脚本
    backend_dir = os.path.join(current_dir, 'backend')
    if os.path.exists(backend_dir) and os.path.isdir(backend_dir):
        for item in os.listdir(backend_dir):
            if item.endswith('.py') and (item.startswith('check_') or 
                                        item.startswith('create_') or
                                        item.startswith('fix_') or
                                        item.startswith('test_') or
                                        item.startswith('run_') and item != 'run.py'):
                try:
                    os.remove(os.path.join(backend_dir, item))
                    logger.info(f"已删除backend目录中的冗余文件: {item}")
                except Exception as e:
                    logger.error(f"删除文件 {backend_dir}/{item} 时出错: {e}")

    logger.info("文件清理完成")

def fix_database():
    """修复数据库问题"""
    logger.info("开始修复数据库...")
    
    # 检查数据库连接
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False
    
    # 修复users表
    fix_users_table()
    
    # 修复papers表
    fix_papers_table()
    
    # 创建管理员用户
    create_admin_user()
    
    # 检查并创建测试论文
    create_test_paper()
    
    logger.info("数据库修复完成")
    return True

def fix_users_table():
    """修复用户表"""
    inspector = inspect(engine)
    if not inspector.has_table('users'):
        logger.warning("users表不存在，将创建新表")
        # 创建用户表
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR(10) DEFAULT 'USER',
                    fullname VARCHAR(100),
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    avatar_url VARCHAR(255),
                    bio TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    last_login DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            logger.info("users表已创建")
    else:
        # 检查并修复字段
        columns = {col['name'] for col in inspector.get_columns('users')}
        
        with engine.connect() as conn:
            # 修复hashed_password字段
            if 'password' in columns and 'hashed_password' not in columns:
                logger.info("将password字段重命名为hashed_password")
                conn.execute(text("""
                    ALTER TABLE users RENAME TO users_old;
                """))
                
                # 获取原表的所有列，并将password更名为hashed_password
                old_columns = [col for col in inspector.get_columns('users_old')]
                column_defs = []
                select_columns = []
                
                for col in old_columns:
                    col_name = col['name']
                    col_type = str(col['type'])
                    
                    if col_name == 'password':
                        column_defs.append(f"hashed_password {col_type}")
                        select_columns.append("password AS hashed_password")
                    else:
                        column_defs.append(f"{col_name} {col_type}")
                        select_columns.append(col_name)
                
                # 创建新表
                conn.execute(text(f"""
                    CREATE TABLE users (
                        {', '.join(column_defs)}
                    );
                """))
                
                # 复制数据
                conn.execute(text(f"""
                    INSERT INTO users
                    SELECT {', '.join(select_columns)}
                    FROM users_old;
                """))
                
                # 删除旧表
                conn.execute(text("DROP TABLE users_old;"))
                logger.info("password字段已重命名为hashed_password")
            
            # 添加缺失的字段
            if 'is_active' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;"))
                logger.info("is_active字段已添加")
            
            # 其他可能缺失的字段
            for field, field_type in [
                ('first_name', 'VARCHAR(50)'),
                ('last_name', 'VARCHAR(50)'),
                ('fullname', 'VARCHAR(100)'),
                ('avatar_url', 'VARCHAR(255)'),
                ('bio', 'TEXT'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
            ]:
                if field not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {field} {field_type};"))
                        logger.info(f"{field}字段已添加")
                    except Exception as e:
                        logger.warning(f"添加{field}字段时出错: {e}")
            
            conn.commit()

def fix_papers_table():
    """修复论文表"""
    inspector = inspect(engine)
    
    # 检查papers表是否存在
    if not inspector.has_table('papers'):
        logger.warning("papers表不存在，将创建新表")
        # 创建papers表
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    journal TEXT,
                    year INTEGER,
                    doi TEXT,
                    abstract TEXT,
                    pdf_path TEXT,
                    url TEXT,
                    citation_count INTEGER DEFAULT 0,
                    reference_count INTEGER DEFAULT 0,
                    is_public BOOLEAN DEFAULT 1,
                    user_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            logger.info("papers表已创建")
    else:
        # 检查表结构
        existing_columns = {col['name'] for col in inspector.get_columns('papers')}
        
        # 检查是否需要完全重建表
        required_columns = {'title', 'authors', 'journal', 'year', 'doi', 'abstract', 
                           'pdf_path', 'user_id', 'created_at', 'updated_at'}
        missing_core_columns = required_columns - existing_columns
        
        if len(missing_core_columns) > 2:  # 如果缺少多个核心字段，重建表
            logger.warning(f"papers表缺少多个核心字段 {missing_core_columns}，将重建表")
            
            # 重命名现有表为备份
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE papers RENAME TO papers_backup;"))
                conn.commit()
            
            # 创建新表
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE papers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        authors TEXT NOT NULL,
                        journal TEXT,
                        year INTEGER,
                        doi TEXT,
                        abstract TEXT,
                        pdf_path TEXT,
                        url TEXT,
                        citation_count INTEGER DEFAULT 0,
                        reference_count INTEGER DEFAULT 0,
                        is_public BOOLEAN DEFAULT 1,
                        user_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                logger.info("papers表已重建")

            # 尝试从备份表复制数据
            try:
                # 检查备份表的列
                backup_columns = {col['name'] for col in inspector.get_columns('papers_backup')}
                common_columns = backup_columns.intersection(required_columns)
                
                if common_columns:
                    columns_str = ', '.join(common_columns)
                    with engine.connect() as conn:
                        conn.execute(text(f"""
                            INSERT INTO papers ({columns_str})
                            SELECT {columns_str} FROM papers_backup
                        """))
                        conn.commit()
                        logger.info(f"数据已从备份表复制到新表，复制了 {len(common_columns)} 个字段")
            except Exception as e:
                logger.error(f"从备份表复制数据时出错: {e}")
        else:
            # 仅添加缺失字段
            logger.info("修复papers表缺失字段")
            with engine.connect() as conn:
                for column_name, column_type in [
                    ('title', 'TEXT NOT NULL'),
                    ('authors', 'TEXT NOT NULL'),
                    ('journal', 'TEXT'),
                    ('year', 'INTEGER'),
                    ('doi', 'TEXT'),
                    ('abstract', 'TEXT'),
                    ('pdf_path', 'TEXT'),
                    ('url', 'TEXT'),
                    ('citation_count', 'INTEGER DEFAULT 0'),
                    ('reference_count', 'INTEGER DEFAULT 0'),
                    ('is_public', 'BOOLEAN DEFAULT 1'),
                    ('user_id', 'INTEGER'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
                ]:
                    if column_name not in existing_columns:
                        try:
                            conn.execute(text(f"ALTER TABLE papers ADD COLUMN {column_name} {column_type};"))
                            logger.info(f"{column_name}字段已添加")
                        except Exception as e:
                            logger.warning(f"添加{column_name}字段时出错: {e}")
                conn.commit()

def create_admin_user():
    """创建或更新管理员用户"""
    db = SessionLocal()
    try:
        # 检查管理员是否存在
        result = db.execute(text("SELECT id, username, hashed_password FROM users WHERE role = 'ADMIN' LIMIT 1"))
        admin = result.fetchone()
        
        if admin:
            # 更新管理员密码和激活状态
            admin_id = admin[0]
            new_password_hash = pwd_context.hash("password")
            db.execute(text(f"""
                UPDATE users 
                SET hashed_password = '{new_password_hash}', is_active = 1 
                WHERE id = {admin_id}
            """))
            db.commit()
            logger.info(f"管理员用户 {admin[1]} 密码已重置，并设为激活状态")
        else:
            # 创建新的管理员用户
            new_password_hash = pwd_context.hash("password")
            now = datetime.datetime.utcnow().isoformat()
            db.execute(text(f"""
                INSERT INTO users (
                    username, email, hashed_password, role, is_active, created_at, updated_at
                ) VALUES (
                    'admin', 'admin@example.com', '{new_password_hash}', 'ADMIN', 1, '{now}', '{now}'
                )
            """))
            db.commit()
            logger.info("新管理员用户已创建 (username: admin, password: password)")
    except Exception as e:
        db.rollback()
        logger.error(f"创建/更新管理员用户时出错: {e}")
    finally:
        db.close()

def create_test_paper():
    """创建测试论文"""
    db = SessionLocal()
    try:
        # 检查是否已有论文
        result = db.execute(text("SELECT COUNT(*) FROM papers"))
        paper_count = result.scalar()
        
        if paper_count > 0:
            logger.info(f"系统中已有 {paper_count} 篇论文，不再创建测试论文")
            return
        
        # 获取管理员用户ID
        result = db.execute(text("SELECT id FROM users WHERE role = 'ADMIN' LIMIT 1"))
        admin_id = result.scalar()
        
        if not admin_id:
            logger.error("未找到管理员用户，无法创建测试论文")
            return
        
        # 创建测试论文
        now = datetime.datetime.utcnow().isoformat()
        db.execute(text(f"""
            INSERT INTO papers (
                title, authors, journal, year, doi, abstract, user_id, created_at, updated_at
            ) VALUES (
                '测试论文', '测试作者', '测试期刊', 2023, '10.1234/test.123', 
                '这是一篇测试论文的摘要', {admin_id}, '{now}', '{now}'
            )
        """))
        db.commit()
        logger.info("测试论文创建成功")
    except Exception as e:
        db.rollback()
        logger.error(f"创建测试论文时出错: {e}")
    finally:
        db.close()

def ensure_upload_dirs():
    """确保上传目录存在"""
    upload_dir = os.path.join(current_dir, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(os.path.join(upload_dir, "papers"), exist_ok=True)
    os.makedirs(os.path.join(upload_dir, "avatars"), exist_ok=True)
    logger.info(f"上传目录已创建: {upload_dir}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文献管理系统修复工具")
    parser.add_argument("--clean", action="store_true", help="清理冗余文件")
    parser.add_argument("--fix-db", action="store_true", help="修复数据库问题")
    parser.add_argument("--all", action="store_true", help="执行所有修复操作")
    
    args = parser.parse_args()
    
    # 如果没有指定任何参数，默认执行所有操作
    if not any([args.clean, args.fix_db, args.all]):
        args.all = True
    
    if args.clean or args.all:
        clean_duplicate_files()
    
    if args.fix_db or args.all:
        fix_database()
    
    # 确保上传目录存在
    ensure_upload_dirs()
    
    logger.info("所有修复操作已完成")
    logger.info("请使用以下命令启动服务: python run.py --port 8000")

if __name__ == "__main__":
    main() 
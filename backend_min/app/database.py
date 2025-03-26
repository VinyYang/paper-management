from sqlalchemy import create_engine, event, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import logging
import time
from sqlalchemy import text

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# 兼容配置: 检查SQLAlchemy版本
import sqlalchemy
sqlalchemy_version = sqlalchemy.__version__
logger.info(f"使用SQLAlchemy版本: {sqlalchemy_version}")

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

# 依赖项
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 使用统一的模型导入
        # 从models包导入所有模型
        from .models import (
            Base, User, UserRole, Paper, Tag, Note, Concept, 
            ConceptRelation, ReadingHistory, Recommendation, 
            Project, SearchHistory, Journal, LatestPaper, 
            UserInterest, UserActivity, Citation, paper_tag, 
            project_paper, paper_concepts
        )
        
        # 移除删除users表的代码，保留用户数据
        # 确保数据库连接有效
        with engine.connect() as conn:
            # 创建所有表（如果不存在）
            Base.metadata.create_all(bind=engine)
            logger.info("数据库表创建成功")
            
            # 检查users表是否创建成功
            inspector = inspect(engine)
            if not inspector.has_table("users"):
                logger.error("users表未创建成功")
                raise Exception("users表未创建成功")
        
        # 创建初始数据
        db = SessionLocal()
        try:
            # 使用传统的SQLAlchemy查询语法
            # 先尝试创建管理员用户（如果不存在）
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
                
            # 调用创建初始数据的其他函数
            create_initial_data(db)
            logger.info("初始数据创建完成")
        except Exception as e:
            db.rollback()
            logger.error(f"创建初始数据时出错: {e}")
        finally:
            db.close()
            
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

def _check_and_update_schema():
    """检查并更新数据库结构"""
    # 使用反射方式检查表结构
    inspector = inspect(engine)
    
    # 清除缓存，强制刷新表定义
    Base.metadata.clear()
    
    # 重新加载模型类
    # 不要从models导入Base，直接使用当前模块定义的Base
    from .models import (
        User, UserRole, Paper, Tag, Note, Concept, 
        ConceptRelation, ReadingHistory, Recommendation, 
        Project, SearchHistory, Journal, LatestPaper, 
        UserInterest, UserActivity, Citation
    )
    
    # 尝试强制创建缺失的列
    try:
        # 在不删除现有数据的情况下更新表结构
        Base.metadata.create_all(bind=engine)
        logger.info("成功更新表结构")
    except Exception as e:
        logger.error(f"更新表结构失败: {e}")
        
    # 继续执行原有的检查逻辑
    # 检查users表是否存在并检查字段
    if inspector.has_table("users"):
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        # 如果存在password字段但不存在hashed_password字段，需要重命名
        if 'password' in columns and 'hashed_password' not in columns:
            logger.info("重命名users表的password字段为hashed_password...")
            try:
                with engine.connect() as conn:
                    # SQLite不直接支持重命名列，需要创建新表并复制数据
                    # 1. 创建临时表
                    conn.execute(text("""
                        CREATE TABLE users_new (
                            id INTEGER PRIMARY KEY,
                            username VARCHAR(50) NOT NULL UNIQUE,
                            email VARCHAR(100) NOT NULL UNIQUE,
                            hashed_password VARCHAR(255) NOT NULL,
                            role VARCHAR(10),
                            first_name VARCHAR(50),
                            last_name VARCHAR(50),
                            avatar_url VARCHAR(255),
                            fullname VARCHAR(100),
                            bio TEXT,
                            is_active BOOLEAN,
                            last_login DATETIME,
                            created_at DATETIME,
                            updated_at DATETIME
                        )
                    """))
                    
                    # 2. 复制数据，使用password值填充hashed_password
                    conn.execute(text("""
                        INSERT INTO users_new (id, username, email, hashed_password, role, 
                                             first_name, last_name, avatar_url, fullname, bio, is_active, 
                                             last_login, created_at, updated_at)
                        SELECT id, username, email, password, role, 
                               first_name, last_name, avatar, NULL, bio, is_active,
                               last_login, created_at, updated_at
                        FROM users
                    """))
                    
                    # 3. 删除旧表
                    conn.execute(text("DROP TABLE users"))
                    
                    # 4. 重命名新表
                    conn.execute(text("ALTER TABLE users_new RENAME TO users"))
                    
                    conn.commit()
                    logger.info("重命名users表的password字段为hashed_password完成")
            except Exception as e:
                logger.error(f"重命名password字段失败: {e}")
        
        # 如果不存在hashed_password字段，需要添加
        elif 'hashed_password' not in columns and 'password' not in columns:
            logger.info("添加users表的hashed_password字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"))
                    conn.commit()
                    logger.info("添加hashed_password字段完成")
            except Exception as e:
                logger.error(f"添加hashed_password字段失败: {e}")
    
    # 检查papers表是否存在
    if inspector.has_table("papers"):
        # 检查papers表的字段
        columns = [col['name'] for col in inspector.get_columns('papers')]
        
        # 添加journal字段
        if 'journal' not in columns:
            logger.info("添加papers表的journal字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE papers ADD COLUMN journal VARCHAR(255)"))
                    conn.commit()
                    logger.info("添加journal字段完成")
            except Exception as e:
                logger.error(f"添加journal字段失败: {e}")
        
        # 添加doi字段
        if 'doi' not in columns:
            logger.info("添加papers表的doi字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE papers ADD COLUMN doi VARCHAR(100)"))
                    conn.commit()
                    logger.info("添加doi字段完成")
            except Exception as e:
                logger.error(f"添加doi字段失败: {e}")
        
        # 添加url字段
        if 'url' not in columns:
            logger.info("添加papers表的url字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE papers ADD COLUMN url VARCHAR(500)"))
                    conn.commit()
                    logger.info("添加url字段完成")
            except Exception as e:
                logger.error(f"添加url字段失败: {e}")
        
        # 添加source字段
        if 'source' not in columns:
            logger.info("添加papers表的source字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE papers ADD COLUMN source VARCHAR(255)"))
                    conn.commit()
                    logger.info("添加source字段完成")
            except Exception as e:
                logger.error(f"添加source字段失败: {e}")
        
        # 添加publication_date字段
        if 'publication_date' not in columns:
            logger.info("添加papers表的publication_date字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE papers ADD COLUMN publication_date DATETIME"))
                    conn.commit()
                    logger.info("添加publication_date字段完成")
            except Exception as e:
                logger.error(f"添加publication_date字段失败: {e}")
        
        # 添加updated_at字段，如果不存在的话
        if 'updated_at' not in columns:
            logger.info("添加papers表的updated_at字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE papers ADD COLUMN updated_at DATETIME"))
                    conn.commit()
                    logger.info("添加updated_at字段完成")
            except Exception as e:
                logger.error(f"添加updated_at字段失败: {e}")
                
        # 添加file_path字段，如果不存在的话
        if 'file_path' not in columns and 'pdf_path' in columns:
            logger.info("重命名papers表的pdf_path字段为file_path...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE papers ADD COLUMN file_path VARCHAR(500)"))
                    conn.execute(text("UPDATE papers SET file_path = pdf_path"))
                    conn.commit()
                    logger.info("添加file_path字段并复制pdf_path数据完成")
            except Exception as e:
                logger.error(f"处理file_path字段失败: {e}")

    # 检查users表的字段
    inspector = inspect(engine)
    users_columns = [column['name'] for column in inspector.get_columns('users')]
    
    # 将avatar字段重命名为avatar_url，如果需要的话
    if 'avatar' in users_columns and 'avatar_url' not in users_columns:
        logger.info("重命名users表的avatar字段为avatar_url...")
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255)"))
                conn.execute(text("UPDATE users SET avatar_url = avatar"))
                conn.commit()
                logger.info("重命名avatar字段为avatar_url完成")
        except Exception as e:
            logger.error(f"重命名avatar字段失败: {e}")
    elif 'avatar' not in users_columns and 'avatar_url' not in users_columns:
        # 如果两个字段都不存在，直接添加avatar_url
        logger.info("添加users表的avatar_url字段...")
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255)"))
                conn.commit()
                logger.info("添加avatar_url字段完成")
        except Exception as e:
            logger.error(f"添加avatar_url字段失败: {e}")
            
    # 添加fullname字段，如果不存在
    if 'fullname' not in users_columns:
        logger.info("添加users表的fullname字段...")
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN fullname VARCHAR(100)"))
                # 尝试用first_name和last_name拼接填充fullname
                if 'first_name' in users_columns and 'last_name' in users_columns:
                    conn.execute(text("UPDATE users SET fullname = TRIM(COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')) WHERE TRIM(COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')) != ''"))
                conn.commit()
                logger.info("添加fullname字段完成")
        except Exception as e:
            logger.error(f"添加fullname字段失败: {e}")
            
    # 添加其他可能缺失的字段
    missing_columns = {
        'first_name': 'VARCHAR(50)',
        'last_name': 'VARCHAR(50)',
        'bio': 'TEXT',
        'last_login': 'DATETIME'
    }
    
    for col_name, col_type in missing_columns.items():
        if col_name not in users_columns:
            logger.info(f"添加users表的{col_name}字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    logger.info(f"添加{col_name}字段完成")
            except Exception as e:
                logger.error(f"添加{col_name}字段失败: {e}")
    
    # 检查concepts表是否有category字段
    if inspector.has_table("concepts"):
        concepts_columns = [col['name'] for col in inspector.get_columns('concepts')]
        
        # 添加category字段
        if 'category' not in concepts_columns:
            logger.info("添加concepts表的category字段...")
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE concepts ADD COLUMN category INTEGER DEFAULT 0"))
                    conn.commit()
                    logger.info("添加category字段完成")
            except Exception as e:
                logger.error(f"添加category字段失败: {e}")
    
    # 检查latest_papers表是否有doi字段
    if inspector.has_table("latest_papers"):
        latest_papers_columns = [col['name'] for col in inspector.get_columns('latest_papers')]
        
        # 需要添加的字段列表
        latest_papers_missing_cols = {
            'doi': 'VARCHAR(100)',
            'title': 'VARCHAR(500)',
            'authors': 'VARCHAR(1000)',
            'abstract': 'TEXT',
            'url': 'VARCHAR(500)'
        }
        
        for col_name, col_type in latest_papers_missing_cols.items():
            if col_name not in latest_papers_columns:
                logger.info(f"添加latest_papers表的{col_name}字段...")
                try:
                    with engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE latest_papers ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        logger.info(f"添加{col_name}字段完成")
                except Exception as e:
                    logger.error(f"添加{col_name}字段失败: {e}")

def reset_db():
    """重置数据库（仅用于测试）"""
    from . import models  # 导入所有模型
    
    try:
        logger.info("开始重置数据库...")
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        logger.info("数据库表已删除")
        
        # 重新创建表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表已重新创建")
        
        # 创建初始数据
        db = SessionLocal()
        create_initial_data(db)
        logger.info("初始数据创建完成")
        
    except Exception as e:
        logger.error(f"数据库重置失败: {str(e)}")
        raise

def create_initial_data(db):
    """创建初始数据"""
    from .models import User, UserRole, Concept
    from sqlalchemy import text, inspect
    
    try:
        # 检查表是否已创建
        inspector = inspect(db.get_bind())
        
        # 创建管理员用户（如果users表存在）
        if inspector.has_table("users"):
            # 使用原始SQL查询检查是否存在管理员
            admin_exists = db.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'")).scalar()
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
            logger.warning("users表不存在，跳过创建管理员用户")
    
        # 创建初始概念（如果concepts表存在）
        if inspector.has_table("concepts"):
            # 使用原始SQL查询检查是否存在概念
            concepts_exist = db.execute(text("SELECT COUNT(*) FROM concepts")).scalar()
            if not concepts_exist:
                concepts = [
                    Concept(name="机器学习", description="Machine Learning是人工智能的一个分支，涉及算法和统计模型"),
                    Concept(name="深度学习", description="Deep Learning是机器学习的一个分支，使用神经网络处理信息"),
                    Concept(name="计算机视觉", description="Computer Vision是一个研究如何使计算机理解图像和视频的领域"),
                    Concept(name="自然语言处理", description="NLP研究计算机与人类语言的交互"),
                    Concept(name="强化学习", description="Reinforcement Learning是通过与环境交互学习决策的方法")
                ]
                db.add_all(concepts)
                db.commit()
                logger.info("初始概念已创建")
        else:
            logger.warning("concepts表不存在，跳过创建初始概念")
    except Exception as e:
        db.rollback()
        logger.error(f"创建初始数据时出错: {e}") 
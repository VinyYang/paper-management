import sqlite3
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_database():
    """备份数据库"""
    if os.path.exists('app.db'):
        try:
            shutil.copy('app.db', 'app.db.backup')
            logger.info("数据库已备份为app.db.backup")
            return True
        except Exception as e:
            logger.error(f"备份数据库失败: {e}")
            return False
    else:
        logger.warning("数据库文件不存在，无需备份")
        return True

def fix_database():
    """修复数据库表结构"""
    try:
        # 连接到数据库
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # 先清空所有限制
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        # 创建所有必要的表
        tables = {
            # 用户表
            "users": '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) UNIQUE,
                    hashed_password VARCHAR(200) NOT NULL,
                    created_at DATETIME,
                    updated_at DATETIME,
                    role VARCHAR(20) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1
                )
            ''',
            
            # 论文表
            "papers": '''
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    authors VARCHAR(1000),
                    abstract TEXT,
                    doi VARCHAR(100),
                    publication_date DATETIME,
                    journal VARCHAR(200),
                    year INTEGER,
                    citations INTEGER DEFAULT 0,
                    file_path VARCHAR(500),
                    url VARCHAR(500),
                    source VARCHAR(255),
                    created_at DATETIME,
                    updated_at DATETIME,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''',
            
            # 标签表
            "tags": '''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description VARCHAR(200)
                )
            ''',
            
            # 论文-标签关联表
            "paper_tag": '''
                CREATE TABLE IF NOT EXISTS paper_tag (
                    paper_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (paper_id, tag_id),
                    FOREIGN KEY(paper_id) REFERENCES papers(id),
                    FOREIGN KEY(tag_id) REFERENCES tags(id)
                )
            ''',
            
            # 笔记表
            "notes": '''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY,
                    paper_id INTEGER,
                    content TEXT NOT NULL,
                    page_number INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME,
                    user_id INTEGER,
                    FOREIGN KEY(paper_id) REFERENCES papers(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''',
            
            # 概念表
            "concepts": '''
                CREATE TABLE IF NOT EXISTS concepts (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            ''',
            
            # 概念关系表
            "concept_relations": '''
                CREATE TABLE IF NOT EXISTS concept_relations (
                    id INTEGER PRIMARY KEY,
                    source_id INTEGER,
                    target_id INTEGER,
                    relation_type VARCHAR(50),
                    weight FLOAT DEFAULT 1.0,
                    FOREIGN KEY(source_id) REFERENCES concepts(id),
                    FOREIGN KEY(target_id) REFERENCES concepts(id)
                )
            ''',
            
            # 论文-概念关联表
            "paper_concepts": '''
                CREATE TABLE IF NOT EXISTS paper_concepts (
                    paper_id INTEGER,
                    concept_id INTEGER,
                    weight FLOAT DEFAULT 1.0,
                    PRIMARY KEY (paper_id, concept_id),
                    FOREIGN KEY(paper_id) REFERENCES papers(id),
                    FOREIGN KEY(concept_id) REFERENCES concepts(id)
                )
            ''',
            
            # 阅读历史表
            "reading_history": '''
                CREATE TABLE IF NOT EXISTS reading_history (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    paper_id INTEGER,
                    read_time DATETIME,
                    duration INTEGER,
                    interaction_type VARCHAR(50),
                    rating FLOAT,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(paper_id) REFERENCES papers(id)
                )
            ''',
            
            # 推荐表
            "recommendations": '''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    paper_id INTEGER,
                    score FLOAT,
                    reason TEXT,
                    created_at DATETIME,
                    is_read BOOLEAN DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(paper_id) REFERENCES papers(id)
                )
            ''',
            
            # 项目表
            "projects": '''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at DATETIME,
                    updated_at DATETIME,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''',
            
            # 项目-论文关联表
            "project_paper": '''
                CREATE TABLE IF NOT EXISTS project_paper (
                    project_id INTEGER,
                    paper_id INTEGER,
                    PRIMARY KEY (project_id, paper_id),
                    FOREIGN KEY(project_id) REFERENCES projects(id),
                    FOREIGN KEY(paper_id) REFERENCES papers(id)
                )
            ''',
            
            # 搜索历史表
            "search_history": '''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    query VARCHAR(500) NOT NULL,
                    result_info TEXT,
                    doi VARCHAR(100),
                    url VARCHAR(1000),
                    created_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            '''
        }
        
        # 创建所有表
        for table_name, create_sql in tables.items():
            logger.info(f"创建{table_name}表...")
            cursor.execute(create_sql)
        
        # 创建管理员用户（如果不存在）
        cursor.execute("SELECT id FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO users (username, email, hashed_password, role, created_at, updated_at)
            VALUES ('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''')
            logger.info("管理员用户已创建")
        
        # 将外键约束打开
        cursor.execute("PRAGMA foreign_keys=ON")
        
        # 提交更改
        conn.commit()
        logger.info("数据库表创建完成")
        return True
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        logger.error(f"数据库修复失败: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    try:
        import shutil
        # 备份数据库
        backup_database()
    except Exception as e:
        logger.error(f"备份数据库时出错: {e}")
    
    # 修复数据库
    if fix_database():
        print("数据库修复成功！")
    else:
        print("数据库修复失败！") 
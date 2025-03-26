import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保可以导入backend模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

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

def remove_doi_constraint():
    """移除papers表中DOI的唯一性约束"""
    inspector = inspect(engine)
    if not inspector.has_table('papers'):
        logger.error("papers表不存在")
        return False
    
    try:
        # 在SQLite中移除约束的唯一方法是重建表
        with engine.connect() as conn:
            # 1. 获取现有表的所有列
            columns_info = inspector.get_columns('papers')
            column_defs = []
            
            for col in columns_info:
                col_name = col['name']
                col_type = str(col['type'])
                nullable = "" if col.get('nullable', True) else " NOT NULL"
                
                # 主键单独处理
                if col_name == 'id':
                    column_defs.append(f"{col_name} {col_type} PRIMARY KEY")
                else:
                    column_defs.append(f"{col_name} {col_type}{nullable}")
            
            # 2. 创建临时表
            conn.execute(text(f"""
                CREATE TABLE papers_new (
                    {', '.join(column_defs)}
                )
            """))
            
            # 3. 复制数据
            columns = [col['name'] for col in columns_info]
            columns_str = ', '.join(columns)
            
            conn.execute(text(f"""
                INSERT INTO papers_new
                SELECT {columns_str} FROM papers
            """))
            
            # 4. 删除旧表
            conn.execute(text("DROP TABLE papers"))
            
            # 5. 重命名新表
            conn.execute(text("ALTER TABLE papers_new RENAME TO papers"))
            
            conn.commit()
            logger.info("DOI唯一性约束已移除")
            return True
    except Exception as e:
        logger.error(f"移除DOI约束时出错: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始修复papers表DOI约束问题...")
    
    # 检查数据库连接
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return
    
    # 移除DOI约束
    if remove_doi_constraint():
        logger.info("papers表DOI约束修复完成")
    else:
        logger.error("papers表DOI约束修复失败")
    
    logger.info("请重启服务器以应用更改")

if __name__ == "__main__":
    main() 
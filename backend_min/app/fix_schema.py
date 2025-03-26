import sqlite3
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_papers_schema():
    """修复数据库结构，添加缺失的字段"""
    try:
        # 连接到数据库
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # 检查papers表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
        if not cursor.fetchone():
            logger.error("papers表不存在")
            return False
        
        # 检查journal字段是否存在
        cursor.execute("PRAGMA table_info(papers)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # 添加journal字段
        if 'journal' not in column_names:
            logger.info("添加journal字段到papers表...")
            cursor.execute('ALTER TABLE papers ADD COLUMN journal VARCHAR(255);')
            logger.info("journal字段添加成功")
        else:
            # 检查journal字段的类型是否正确
            journal_type = None
            for column in columns:
                if column[1] == 'journal':
                    journal_type = column[2]
                    break
            
            logger.info(f"journal字段已存在，类型为 {journal_type}")
            
            # 尝试重建journal字段，以确保它正确存在于数据库中
            try:
                cursor.execute("SELECT journal FROM papers LIMIT 1")
                logger.info("journal字段可以正常查询")
            except Exception as e:
                logger.error(f"journal字段查询出错: {e}")
                logger.info("尝试修复journal字段...")
                
                # 创建临时表
                cursor.execute('''
                CREATE TABLE papers_temp AS 
                SELECT id, title, authors, abstract, doi, publication_date, 
                       '' as journal, file_path, url, source, created_at, updated_at, user_id,
                       year, citations
                FROM papers
                ''')
                
                # 删除原表
                cursor.execute('DROP TABLE papers')
                
                # 重命名临时表
                cursor.execute('ALTER TABLE papers_temp RENAME TO papers')
                
                logger.info("journal字段修复完成")
            
        # 检查其他可能缺失的字段
        if 'year' not in column_names:
            logger.info("添加year字段到papers表...")
            cursor.execute('ALTER TABLE papers ADD COLUMN year INTEGER;')
            logger.info("year字段添加成功")
        
        if 'citations' not in column_names:
            logger.info("添加citations字段到papers表...")
            cursor.execute('ALTER TABLE papers ADD COLUMN citations INTEGER DEFAULT 0;')
            logger.info("citations字段添加成功")
            
        # 提交更改
        conn.commit()
        logger.info("数据库结构修复完成")
        return True
    except Exception as e:
        logger.error(f"修复数据库结构时出错: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if fix_papers_schema():
        print("数据库结构修复成功")
    else:
        print("数据库结构修复失败") 
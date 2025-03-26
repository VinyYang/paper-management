import os
import sys
import logging
import sqlite3

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保可以导入backend模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 数据库路径
DB_PATH = os.path.join(current_dir, 'app.db')

def check_tables():
    """检查数据库表结构"""
    if not os.path.exists(DB_PATH):
        logger.error(f"数据库文件不存在: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"数据库中共有 {len(tables)} 个表:")
        for table in tables:
            table_name = table[0]
            logger.info(f"表名: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            logger.info(f"  - 列数: {len(columns)}")
            for col in columns:
                col_id, col_name, col_type, not_null, default_value, is_pk = col
                logger.info(f"  - 列名: {col_name}, 类型: {col_type}, 非空: {bool(not_null)}, 默认值: {default_value}, 主键: {bool(is_pk)}")
            
            # 获取表索引
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            logger.info(f"  - 索引数: {len(indexes)}")
            for idx in indexes:
                idx_seq, idx_name, idx_unique = idx[:3]
                logger.info(f"  - 索引名: {idx_name}, 唯一: {bool(idx_unique)}")
                
                # 获取索引详情
                cursor.execute(f"PRAGMA index_info({idx_name})")
                idx_cols = cursor.fetchall()
                idx_col_names = [cursor.execute(f"PRAGMA table_info({table_name})").fetchall()[col[1]][1] for col in idx_cols]
                logger.info(f"    - 索引列: {', '.join(idx_col_names)}")
            
        conn.close()
    except Exception as e:
        logger.error(f"检查数据库结构时出错: {e}")

def check_papers_doi():
    """特别检查papers表中的DOI字段是否有唯一约束"""
    if not os.path.exists(DB_PATH):
        logger.error(f"数据库文件不存在: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查papers表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
        if not cursor.fetchone():
            logger.error("papers表不存在")
            conn.close()
            return
        
        # 检查papers表的索引
        cursor.execute("PRAGMA index_list(papers)")
        indexes = cursor.fetchall()
        doi_unique = False
        
        for idx in indexes:
            idx_name = idx[1]
            idx_unique = idx[2]
            
            if idx_unique:
                # 检查这个唯一索引包含的列
                cursor.execute(f"PRAGMA index_info({idx_name})")
                idx_cols = cursor.fetchall()
                idx_col_names = [cursor.execute("PRAGMA table_info(papers)").fetchall()[col[1]][1] for col in idx_cols]
                
                if 'doi' in idx_col_names and len(idx_col_names) == 1:
                    doi_unique = True
                    logger.info(f"发现DOI唯一约束: {idx_name}")
        
        if not doi_unique:
            logger.info("papers表中的DOI字段没有唯一约束")
        
        # 测试插入重复DOI
        test_doi = '10.1234/test.123'  # 使用一个测试DOI
        try:
            # 首先删除测试记录
            cursor.execute("DELETE FROM papers WHERE doi = ?", (test_doi,))
            
            # 插入第一条记录
            cursor.execute("""
                INSERT INTO papers (title, authors, doi, year)
                VALUES (?, ?, ?, ?)
            """, ('测试论文1', '测试作者', test_doi, 2023))
            
            # 尝试插入第二条相同DOI的记录
            cursor.execute("""
                INSERT INTO papers (title, authors, doi, year)
                VALUES (?, ?, ?, ?)
            """, ('测试论文2', '测试作者', test_doi, 2023))
            
            # 如果能执行到这里，说明没有唯一约束
            logger.info("DOI唯一性测试通过：可以插入重复DOI")
            conn.rollback()  # 回滚测试数据
        except sqlite3.IntegrityError as e:
            logger.error(f"DOI唯一性测试失败：{e}")
            logger.info("papers表中的DOI字段仍有唯一约束")
            conn.rollback()
        
        conn.close()
    except Exception as e:
        logger.error(f"检查papers表DOI约束时出错: {e}")

if __name__ == "__main__":
    logger.info("开始检查数据库结构...")
    check_tables()
    logger.info("\n专门检查papers表的DOI约束:")
    check_papers_doi()
    logger.info("数据库检查完成") 
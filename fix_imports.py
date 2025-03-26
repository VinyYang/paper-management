import os
import re

def fix_imports_in_file(file_path):
    """修复文件中的导入路径，将from app.替换为from .."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换导入
    modified_content = re.sub(r'from\s+app\.', 'from ..', content)
    
    # 如果有修改，写回文件
    if modified_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"已修复: {file_path}")
        return True
    return False

def scan_directory(directory):
    """扫描目录下所有Python文件并修复导入"""
    fixed_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                
                # 特殊处理main.py，因为它是入口点
                if os.path.basename(file_path) == "main.py":
                    continue
                    
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    
    return fixed_count

if __name__ == "__main__":
    app_dir = os.path.join("backend", "app")
    fixed_count = scan_directory(app_dir)
    print(f"总共修复了 {fixed_count} 个文件") 
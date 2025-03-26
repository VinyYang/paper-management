import os
import shutil
import sys
from datetime import datetime

def create_directory(directory):
    """创建目录(如果不存在)"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")

def copy_file(src, dst):
    """复制文件，保持目录结构"""
    # 确保目标目录存在
    dst_dir = os.path.dirname(dst)
    create_directory(dst_dir)
    
    # 复制文件
    try:
        shutil.copy2(src, dst)
        print(f"复制文件: {src} -> {dst}")
    except Exception as e:
        print(f"复制文件 {src} 失败: {str(e)}")

def copy_directory(src, dst, ignore_patterns=None):
    """复制整个目录，保持目录结构"""
    try:
        if ignore_patterns:
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore_patterns), dirs_exist_ok=True)
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"复制目录: {src} -> {dst}")
    except Exception as e:
        print(f"复制目录 {src} 失败: {str(e)}")

def save_core_code(output_dir="DS_core"):
    """保存DS项目的核心代码"""
    # 获取当前时间作为目录名的一部分
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"{output_dir}_{timestamp}"
    
    # 基本路径
    current_dir = os.getcwd()
    frontend_dir = os.path.join(current_dir, "frontend")
    backend_dir = os.path.join(current_dir, "backend")
    
    # 创建主输出目录
    create_directory(output_dir)
    
    # 前端核心文件和目录
    frontend_core = [
        "src/components",
        "src/pages",
        "src/contexts",
        "src/services",
        "src/api",
        "src/utils",
        "src/types",
        "src/App.tsx",
        "src/App.css",
        "src/index.tsx",
        "src/config.ts",
        "package.json",
        "tsconfig.json",
        "public"
    ]
    
    # 后端核心文件和目录
    backend_core = [
        "app/routers",
        "app/schemas",
        "app/services",
        "app/utils",
        "app/crud",
        "app/auth",
        "app/dependencies.py",
        "app/main.py",
        "app/models.py",
        "app/database.py",
        "app/config.py",
        "requirements.txt"
    ]
    
    # 复制前端核心文件
    for item in frontend_core:
        src_path = os.path.join(frontend_dir, item)
        dst_path = os.path.join(output_dir, "frontend", item)
        
        if os.path.isdir(src_path):
            copy_directory(src_path, dst_path, ["node_modules", "__pycache__", "*.pyc", "*.pyo", ".git"])
        elif os.path.isfile(src_path):
            copy_file(src_path, dst_path)
    
    # 复制后端核心文件
    for item in backend_core:
        src_path = os.path.join(backend_dir, item)
        dst_path = os.path.join(output_dir, "backend", item)
        
        if os.path.isdir(src_path):
            copy_directory(src_path, dst_path, ["__pycache__", "*.pyc", "*.pyo", ".git"])
        elif os.path.isfile(src_path):
            copy_file(src_path, dst_path)
    
    # 创建README文件
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# DS 项目核心代码

这个目录包含了DS项目的核心代码，主要是与网页相关的前端和后端组件。

## 目录结构

- `frontend/`: 前端React应用代码
  - `src/components/`: React组件
  - `src/pages/`: 页面组件
  - `src/contexts/`: React上下文
  - `src/services/`: 服务相关代码
  - `src/api/`: API调用相关代码
  - `src/utils/`: 工具函数
  - `src/App.tsx`: 主应用组件
  - `package.json`: 依赖配置

- `backend/`: 后端FastAPI应用代码
  - `app/routers/`: API路由
  - `app/schemas/`: 数据验证模式
  - `app/services/`: 服务层
  - `app/crud/`: 数据库操作
  - `app/models.py`: 数据库模型
  - `app/main.py`: 主应用
  - `app/dependencies.py`: 依赖
  - `requirements.txt`: 依赖配置

## 导出时间

这个代码导出于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""")
    
    print(f"\n核心代码已保存到 {output_dir} 目录")
    print(f"总大小: {get_dir_size(output_dir):.2f} MB")

def get_dir_size(path):
    """获取目录大小(MB)"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # 转换为MB

if __name__ == "__main__":
    # 获取命令行参数作为输出目录(可选)
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "DS_core"
    save_core_code(output_dir) 
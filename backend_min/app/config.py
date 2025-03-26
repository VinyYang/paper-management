import os
from pathlib import Path
from typing import List

from pydantic import validator, field_validator, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置"""
    # 数据库配置
    DATABASE_URL: str = "sqlite:///app.db"
    SQLALCHEMY_DATABASE_URL: str = DATABASE_URL  # 兼容性字段
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 上传目录
    UPLOAD_DIRECTORY: str = str(BASE_DIR / "uploads")
    
    # API密钥
    EASYSCHOLAR_API_KEY: str = ""
    
    # CORS设置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://127.0.0.1:3000", "http://127.0.0.1:8000", "http://127.0.0.1:8001"]
    
    # 服务配置
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 期刊服务配置
    JOURNAL_CACHE_TIMEOUT: int = 3600  # 缓存超时时间（秒）
    JOURNAL_MAX_CACHE_USES: int = 3  # 最大缓存使用次数
    JOURNAL_FORCE_REFRESH_PROBABILITY: float = 0.1  # 每次请求强制刷新数据的概率（0-1之间）
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """解析允许的源列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # 允许额外字段
    )


# 创建全局设置实例
settings = Settings() 
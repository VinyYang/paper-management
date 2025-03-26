import os
import logging
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException
import uuid
import math
from typing import Optional
from ..config import settings
from sqlalchemy.orm import Session
from pathlib import Path
import aiofiles

from ..models import Paper
from .paper_service import PaperService

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, upload_dir: str = "uploads"):
        self.paper_service = PaperService()
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def upload_pdf(self, db: Session, paper_id: int, file: UploadFile, user_id: int) -> Optional[str]:
        """上传PDF文件"""
        try:
            # 检查论文是否存在且属于当前用户
            paper = self.paper_service.get_paper(db, paper_id, user_id)
            if not paper:
                return None
            
            # 确保上传目录存在
            user_dir = self.upload_dir / str(user_id)
            user_dir.mkdir(exist_ok=True)
            
            # 设置文件保存路径
            file_path = user_dir / f"paper_{paper_id}.pdf"
            
            # 异步保存文件
            try:
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
            except Exception as e:
                logger.error(f"文件写入失败: {e}")
                raise
            
            # 更新论文记录
            pdf_url = f"/uploads/{user_id}/paper_{paper_id}.pdf"
            paper.pdf_url = pdf_url
            paper.has_pdf = True
            db.commit()
            
            return pdf_url
        except Exception as e:
            db.rollback()
            logger.error(f"上传PDF失败: {e}")
            raise
    
    def get_pdf_path(self, db: Session, paper_id: int, user_id: int) -> Optional[str]:
        """获取PDF文件的物理路径"""
        # 检查论文是否存在且属于当前用户
        paper = self.paper_service.get_paper(db, paper_id, user_id)
        if not paper or not paper.has_pdf:
            return None
        
        # 构建文件路径
        file_path = self.upload_dir / str(user_id) / f"paper_{paper_id}.pdf"
        
        if not file_path.exists():
            return None
        
        return str(file_path)
    
    def delete_pdf(self, db: Session, paper_id: int, user_id: int) -> bool:
        """删除PDF文件"""
        try:
            # 检查论文是否存在且属于当前用户
            paper = self.paper_service.get_paper(db, paper_id, user_id)
            if not paper or not paper.has_pdf:
                return False
            
            # 构建文件路径
            file_path = self.upload_dir / str(user_id) / f"paper_{paper_id}.pdf"
            
            # 删除文件
            if file_path.exists():
                os.remove(file_path)
            
            # 更新论文记录
            paper.pdf_url = None
            paper.has_pdf = False
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"删除PDF失败: {e}")
            raise
    
    def get_user_storage_info(self, db: Session, user_id: int) -> dict:
        """获取用户存储信息"""
        try:
            # 默认限制为1GB
            storage_capacity = 1024 * 1024 * 1024
            
            # 计算已用空间
            user_dir = self.upload_dir / str(user_id)
            storage_used = 0
            
            if user_dir.exists():
                for file_path in user_dir.glob("**/*"):
                    if file_path.is_file():
                        storage_used += file_path.stat().st_size
            
            # 计算剩余空间和使用百分比
            storage_free = max(0, storage_capacity - storage_used)
            usage_percentage = (storage_used / storage_capacity) * 100 if storage_capacity > 0 else 0
            
            return {
                "storage_capacity": storage_capacity,
                "storage_used": storage_used,
                "storage_free": storage_free,
                "usage_percentage": usage_percentage
            }
        except Exception as e:
            logger.error(f"获取存储信息失败: {e}")
            raise

    def save_paper(self, file_content, filename=None, doi=None):
        """保存论文文件"""
        try:
            if doi:
                # 如果提供了DOI，使用DOI作为文件名
                safe_filename = f"{doi.replace('/', '_').replace(':', '_')}.pdf"
            elif filename:
                # 如果提供了文件名，生成安全的文件名
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                safe_filename = f"{name}_{timestamp}{ext}"
            else:
                # 生成随机文件名
                safe_filename = f"{uuid.uuid4()}.pdf"
            
            # 完整路径
            file_path = os.path.join(self.upload_dir, safe_filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # 计算文件大小（MB）
            file_size_mb = self.get_file_size_mb(file_path)
            
            logger.info(f"论文文件已保存: {file_path}, 大小: {file_size_mb}MB")
            return file_path, file_size_mb
        except Exception as e:
            logger.error(f"保存论文文件失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    async def save_uploaded_paper(self, file: UploadFile, user=None):
        """保存上传的论文文件，并计算文件大小"""
        try:
            # 检查用户存储空间
            if user:
                # 确保用户有storage_used和storage_capacity属性
                if not hasattr(user, 'storage_used') or user.storage_used is None:
                    user.storage_used = 0
                    logger.info(f"为用户 {user.username} 设置默认storage_used=0")
                
                if not hasattr(user, 'storage_capacity') or user.storage_capacity is None:
                    user.storage_capacity = 1024
                    logger.info(f"为用户 {user.username} 设置默认storage_capacity=1024")
                
                content = await file.read()
                file_size_mb = len(content) / (1024 * 1024)  # 转换为MB
                
                # 检查用户剩余空间
                if user.storage_used + file_size_mb > user.storage_capacity:
                    raise HTTPException(
                        status_code=413,
                        detail=f"存储空间不足！当前已使用 {user.storage_used:.2f}MB，剩余 {user.storage_capacity - user.storage_used:.2f}MB，文件大小 {file_size_mb:.2f}MB"
                    )
            else:
                content = await file.read()
                file_size_mb = len(content) / (1024 * 1024)  # 转换为MB
            
            # 生成安全的文件名
            original_filename = file.filename
            name, ext = os.path.splitext(original_filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_filename = f"{name}_{timestamp}{ext}"
            
            # 完整路径
            file_path = os.path.join(self.upload_dir, safe_filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"上传的论文文件已保存: {file_path}, 大小: {file_size_mb:.2f}MB")
            return file_path, math.ceil(file_size_mb)  # 向上取整，确保不会低估文件大小
        except HTTPException as he:
            # 直接重新抛出HTTP异常
            raise he
        except Exception as e:
            logger.error(f"保存上传论文文件失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    
    async def save_avatar(self, file: UploadFile, user_id: int):
        """保存用户头像"""
        try:
            # 生成安全的文件名
            _, ext = os.path.splitext(file.filename)
            safe_filename = f"avatar_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            
            # 完整路径
            file_path = os.path.join(self.upload_dir, safe_filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"用户头像已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存用户头像失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"头像上传失败: {str(e)}")
    
    def delete_file(self, file_path):
        """删除文件"""
        try:
            if os.path.exists(file_path):
                # 获取文件大小
                file_size_mb = self.get_file_size_mb(file_path)
                
                # 删除文件
                os.remove(file_path)
                logger.info(f"文件已删除: {file_path}, 释放空间: {file_size_mb}MB")
                return file_size_mb
            return 0
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            return 0
    
    def get_file_size_mb(self, file_path):
        """获取文件大小（MB）"""
        try:
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)  # 转换为MB
            return math.ceil(size_mb)  # 向上取整
        except Exception as e:
            logger.error(f"获取文件大小失败: {str(e)}")
            return 0 
import os
import logging
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException
import uuid
from ..config import settings

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, upload_dir=None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIRECTORY
        self.papers_dir = os.path.join(self.upload_dir, "papers")
        self.avatars_dir = os.path.join(self.upload_dir, "avatars")
        
        # 创建目录
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.papers_dir, exist_ok=True)
        os.makedirs(self.avatars_dir, exist_ok=True)
    
    def save_paper(self, file_content, filename=None, doi=None):
        """保存论文文件"""
        try:
            if doi:
                # 如果提供了DOI，使用DOI作为文件名
                safe_filename = f"{doi.replace('/', '_')}.pdf"
            elif filename:
                # 如果提供了文件名，生成安全的文件名
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                safe_filename = f"{name}_{timestamp}{ext}"
            else:
                # 生成随机文件名
                safe_filename = f"{uuid.uuid4()}.pdf"
            
            # 完整路径
            file_path = os.path.join(self.papers_dir, safe_filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"论文文件已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存论文文件失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    async def save_uploaded_paper(self, file: UploadFile):
        """保存上传的论文文件"""
        try:
            # 生成安全的文件名
            original_filename = file.filename
            name, ext = os.path.splitext(original_filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_filename = f"{name}_{timestamp}{ext}"
            
            # 完整路径
            file_path = os.path.join(self.papers_dir, safe_filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"上传的论文文件已保存: {file_path}")
            return file_path
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
            file_path = os.path.join(self.avatars_dir, safe_filename)
            
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
                os.remove(file_path)
                logger.info(f"文件已删除: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            return False 
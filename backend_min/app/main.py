import os
import logging
import httpx
import uuid
import shutil
from typing import List, Optional, Dict, Any, Union
from datetime import timedelta, datetime
import pydantic
import time
import random
import traceback
from io import BytesIO
import json
import re
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status, Query, BackgroundTasks, Request, Response, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import uvicorn
import requests

logger = logging.getLogger(__name__)

from .database import get_db, init_db, create_initial_data, _check_and_update_schema
# 从重构后的模型包导入所需的所有模型类
from .models import Base, User, UserRole, Paper, Note, Tag, Journal, LatestPaper, Project, Recommendation, SearchHistory, UserActivity
from .config import settings
from .dependencies import get_current_user, get_current_admin, create_access_token

# 导入需要的模式类
from .schemas.user import UserProfile, User as UserSchema, UserUpdate, Token

# 导入服务类
from .services.pdf_service import PDFService
from .services.scihub_service import SciHubService
from .services.easyscholar_service import EasyScholarService
from .services.knowledge_graph_service import KnowledgeGraphService
from .services.recommendation_service import RecommendationService
from .services.journal_service import JournalService
from .services.file_service import FileService
from .services.history_service import HistoryService
from app.services.user_service import UserService
from app.services.document_service import DocumentService
from app.services.search_service import SearchService
from app.services.publication_rank_service import PublicationRankService

# 导入路由模块
from .routers import papers, users, notes, knowledge_graph, recommendations, projects, publication_rank

# 仅保留必要的模型导入，其他模型需要时再导入
# 避免导入循环问题
# from .schemas.user import (
#     UserCreate, User as UserSchema, Token, UserUpdate, UserProfile
# )

# 创建应用实例
app = FastAPI(
    title="文献管理系统API",
    description="提供文献管理、笔记记录和知识图谱功能的API",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # 使用配置中的允许源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"]  # 允许暴露所有响应头
)

# 创建上传目录
UPLOAD_DIR = settings.UPLOAD_DIRECTORY
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 初始化服务
pdf_service = PDFService()
scihub_service = SciHubService()
easyscholar_service = EasyScholarService()
knowledge_graph_service = KnowledgeGraphService()
recommendation_service = RecommendationService()
journal_service = JournalService()
file_service = FileService(upload_dir=UPLOAD_DIR)
history_service = HistoryService()
user_service = UserService()
document_service = DocumentService()
search_service = SearchService()
kg_service = KnowledgeGraphService()
publication_rank_service = PublicationRankService()

# 挂载路由
app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(knowledge_graph.router, prefix="/api/graph", tags=["knowledge_graph"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(publication_rank.router, prefix="/api/publication-rank", tags=["publication_rank"])

# 添加直接登录路由，确保路径正确
@app.post("/api/token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """直接提供登录功能的路由，路径为 /api/token"""
    try:
        # 调用用户路由中的登录逻辑
        from .routers.users import login_for_access_token
        return await login_for_access_token(form_data, db)
    except Exception as e:
        logger.error(f"主路由登录失败: {str(e)}")
        # 如果已经是HTTPException则直接抛出
        if isinstance(e, HTTPException):
            raise e
        # 否则包装成HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录处理失败，服务器内部错误"
        )

@app.on_event("startup")
async def startup_event():
    """应用程序启动时执行的操作"""
    try:
        logger.info("开始准备上传目录...")
        # 创建必要的上传目录
        os.makedirs(os.path.join(UPLOAD_DIR, "papers"), exist_ok=True)
        os.makedirs(os.path.join(UPLOAD_DIR, "avatars"), exist_ok=True)
        logger.info("上传目录创建完成")
        
        # 检查并更新数据库模式
        try:
            logger.info("检查并更新数据库结构...")
            _check_and_update_schema()
            logger.info("数据库结构检查完成")
        except Exception as e:
            logger.error(f"数据库结构更新失败: {str(e)}")
            
        logger.info("应用启动成功")
    except Exception as e:
        logger.error(f"启动事件处理失败: {str(e)}")
        # 应用继续运行，但日志记录错误

# 基础路由
@app.get("/")
async def root():
    return {"message": "欢迎使用文献管理系统"}

# 文献管理相关路由
@app.get("/api/papers/search")
async def search_paper(
    doi: str,
    metadata_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 首先检查数据库中是否已存在该DOI的论文
    paper = db.query(Paper).filter(Paper.doi == doi).first()
    
    if paper:
        return paper
    
    try:
        # 使用CrossRef API查询论文信息
        response = httpx.get(f"https://api.crossref.org/works/{doi}")
        response.raise_for_status()
        data = response.json()["message"]
        
        # 提取论文信息
        paper_info = {
            "title": data.get("title", ["Unknown Title"])[0],
            "authors": ", ".join([f"{a.get('given', '')} {a.get('family', '')}" for a in data.get("author", [])]),
            "journal": data.get("container-title", [""])[0] if data.get("container-title") else "",
            "year": int(data.get("published", {}).get("date-parts", [[0]])[0][0]) if data.get("published") else None,
            "doi": doi,
            "abstract": data.get("abstract", "")
        }
        
        # 如果不需要尝试下载PDF，直接返回元数据
        if metadata_only:
            return paper_info
            
        # 尝试从Sci-Hub获取PDF并保存
        if file_service and scihub_service:
            try:
                # 获取PDF下载链接
                pdf_url = scihub_service.get_pdf_url(doi)
                if pdf_url:
                    # 下载PDF
                    pdf_content = scihub_service.download_pdf(pdf_url)
                    if pdf_content:
                        # 保存PDF
                        file_path = file_service.save_paper(pdf_content, doi)
                        paper_info["pdf_path"] = file_path
            except Exception as e:
                # 这里不抛出异常，即使PDF获取失败也返回元数据
                print(f"PDF获取或保存失败: {e}")
        
        return paper_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"论文信息获取失败: {str(e)}")

# Sci-Hub集成
@app.get("/api/scihub/{doi}")
async def get_paper_from_scihub(doi: str):
    """临时禁用Sci-Hub集成"""
    # 返回预设数据，避免API调用
    return {
        "title": "暂时无法获取论文信息",
        "authors": "",
        "doi": doi,
        "pdf_url": ""
    }

# 知识图谱相关路由
@app.get("/api/knowledge-graph")
async def get_knowledge_graph():
    """获取知识图谱数据"""
    try:
        graph_data = knowledge_graph_service.get_graph_data()
        return {"graph": graph_data}
    except Exception as e:
        logger.error(f"获取知识图谱数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取知识图谱数据失败")

@app.get("/api/papers/{paper_id}/graph")
async def get_paper_graph(paper_id: int):
    """获取单个文献的知识关联图"""
    try:
        graph_data = knowledge_graph_service.get_paper_graph(paper_id)
        return {"graph": graph_data}
    except Exception as e:
        logger.error(f"获取文献知识图谱失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取文献知识图谱失败")

# 笔记系统相关路由
@app.get("/api/notes")
async def get_notes(db: Session = Depends(get_db)):
    notes = db.query(Note).all()
    return {"notes": notes}

@app.get("/api/papers/{paper_id}/pdf")
async def get_paper_pdf(paper_id: int, db: Session = Depends(get_db)):
    """获取PDF文件"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    if not paper.pdf_path or not os.path.exists(paper.pdf_path):
        raise HTTPException(status_code=404, detail="PDF文件不存在")
    
    # 从完整路径中提取文件名
    filename = os.path.basename(paper.pdf_path)
    
    return FileResponse(
        paper.pdf_path,
        media_type="application/pdf",
        filename=f"{paper.title}.pdf"
    )

# 用户管理相关路由
@app.get("/api/users/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    paper_count = db.query(Paper).filter(Paper.user_id == current_user.id).count()
    note_count = db.query(Note).filter(Note.user_id == current_user.id).count()
    
    return {
        **current_user.__dict__,
        "paper_count": paper_count,
        "note_count": note_count
    }

@app.put("/api/users/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    if user_update.username and user_update.username != current_user.username:
        # 检查用户名是否已存在
        db_user = db.query(User).filter(User.username == user_update.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    if user_update.email and user_update.email != current_user.email:
        # 检查邮箱是否已存在
        db_user = db.query(User).filter(User.email == user_update.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    # 更新用户信息
    for field, value in user_update.dict(exclude_unset=True).items():
        if field == "password":
            setattr(current_user, "hashed_password", get_password_hash(value))
        else:
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/api/users", response_model=List[UserSchema])
async def get_users(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有用户(仅管理员)"""
    return db.query(User).all()

@app.put("/api/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新用户信息(仅管理员)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user_update.username and user_update.username != user.username:
        db_user = db.query(User).filter(User.username == user_update.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    if user_update.email and user_update.email != user.email:
        db_user = db.query(User).filter(User.email == user_update.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        if field == "password":
            setattr(user, "hashed_password", get_password_hash(value))
        else:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除用户(仅管理员)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账户")
    
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}

# 搜索历史API路由
@app.get("/api/search-history")
async def get_search_history(
    limit: Optional[int] = 10, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的搜索历史"""
    histories = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(SearchHistory.created_at.desc()).limit(limit).all()
    
    return histories

@app.post("/api/search-history")
async def create_search_history(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建搜索历史记录"""
    try:
        search_history = SearchHistory(
            user_id=current_user.id,
            query=data.get("query", ""),
            result_info=data.get("result_info"),
            doi=data.get("doi"),
            url=data.get("url")
        )
        
        db.add(search_history)
        db.commit()
        db.refresh(search_history)
        
        return search_history
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建搜索历史失败: {str(e)}")

# 文件下载路由
@app.get("/api/papers/{paper_id}/download")
async def download_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载论文文件
    """
    # 查找论文
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id  # 确保只能下载自己的文献
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在或无权访问"
        )
    
    if not paper.pdf_path or not os.path.exists(paper.pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文文件不存在"
        )
    
    # 从完整路径中提取文件名
    filename = os.path.basename(paper.pdf_path)
    
    # 返回文件
    return FileResponse(
        path=paper.pdf_path, 
        filename=filename,
        media_type="application/pdf"
    )

# SciHub下载
@app.get("/api/scihub/download/{doi}")
async def download_from_scihub(
    doi: str, 
    current_user: User = Depends(get_current_user)
):
    """从SciHub下载论文"""
    try:
        # 记录访问历史
        await history_service.add_history(
            user_id=current_user.id,
            action_type="download",
            content=f"从SciHub下载论文，DOI: {doi}"
        )
        
        # 获取论文PDF链接
        scihub_service = SciHubService()
        paper_info = await scihub_service.get_paper_by_doi(doi)
        
        if not paper_info:
            raise HTTPException(
                status_code=404,
                detail="无法从SciHub获取论文信息"
            )
            
        # 检查是否找到PDF链接
        if not paper_info.get("pdf_url"):
            raise HTTPException(
                status_code=404,
                detail="未找到PDF链接，请使用备用下载选项"
            )
        
        # 下载PDF内容而不是重定向
        try:
            pdf_content = await scihub_service.download_pdf_async(paper_info["pdf_url"])
            if not pdf_content:
                raise HTTPException(
                    status_code=404,
                    detail="PDF下载失败，请使用备用下载选项"
                )
            
            # 返回PDF内容
            filename = f"{doi.replace('/', '_')}.pdf"
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        except Exception as e:
            logging.error(f"PDF下载失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"PDF下载失败: {str(e)}"
            )
        
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        logging.error(f"SciHub下载失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"SciHub下载失败: {str(e)}"
        )

# 期刊等级查询路由 - 删除此路由，使用路由模块中的实现
# @app.get("/api/publication-rank/{publication_name}")
# async def get_publication_rank(
#     publication_name: str,
#     current_user: User = Depends(get_current_user)
# ):
#     """查询期刊等级"""
#     # 临时返回空数据，避免API调用卡住
#     return {"name": publication_name, "rank": "暂时无法获取", "message": "服务临时禁用"}

# 谷歌学术代理
@app.get("/api/scholar-proxy")
async def scholar_proxy(
    q: str, 
    current_user: User = Depends(get_current_user)
):
    """Google Scholar代理"""
    try:
        # 记录搜索历史
        await history_service.add_history(
            user_id=current_user.id,
            action_type="search",
            content=f"谷歌学术搜索: {q}"
        )
        
        # 使用会话和代理请求Google Scholar
        from .services.scholar_service import GoogleScholarService
        scholar_service = GoogleScholarService()
        result = await scholar_service.search(q)
        
        # 检查搜索是否成功
        if not result["success"]:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": result["error"] or "谷歌学术搜索失败，镜像站点不可用",
                    "query": q
                }
            )
            
        # 返回搜索结果
        return JSONResponse(
            content={
                "success": True,
                "html": result["html"],
                "url": result["url"],
                "source": result["source"],
                "originalTitle": result["originalTitle"],
                "originalAuthor": result["originalAuthor"]
            }
        )
        
    except Exception as e:
        logging.error(f"谷歌学术代理失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"谷歌学术代理异常: {str(e)}",
                "query": q
            }
        )

# 期刊管理相关路由
@app.get("/api/journals", response_model=List[dict])
def get_journals(db: Session = Depends(get_db)):
    """获取所有期刊列表"""
    try:
        journals = journal_service.get_all_journals(db)
        return journals
    except Exception as e:
        logger.error(f"获取期刊列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取期刊列表失败")

@app.get("/api/journals/initialize")
def initialize_journals(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """初始化期刊数据"""
    background_tasks.add_task(journal_service.init_journals, db)
    return {"status": "success", "message": "success"}

@app.get("/api/latest-papers", response_model=List[dict])
def get_latest_papers(category: Optional[str] = None, limit: int = 10, db: Session = Depends(get_db)):
    """获取最新论文列表，可按类别筛选"""
    try:
        papers = journal_service.get_latest_papers(db, category, limit)
        return papers
    except Exception as e:
        logger.error(f"获取最新论文列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取最新论文列表失败")

@app.post("/api/latest-papers/refresh")
def refresh_latest_papers(background_tasks: BackgroundTasks, limit: int = 3, db: Session = Depends(get_db)):
    """刷新最新论文数据"""
    background_tasks.add_task(journal_service.refresh_latest_papers, db, limit)
    return {"status": "success", "message": "论文刷新任务已启动"}

@app.post("/api/latest-papers/force-refresh")
def force_refresh_latest_papers(background_tasks: BackgroundTasks, limit: int = 3, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """强制刷新最新论文数据（不使用缓存）"""
    # 所有用户都可以强制刷新
    # if current_user.role not in [UserRole.ADMIN, UserRole.RESEARCHER]:
    #     raise HTTPException(status_code=403, detail="权限不足，只有管理员或研究人员可以强制刷新数据")
    
    background_tasks.add_task(journal_service.force_refresh_latest_papers, db, limit)
    return {"status": "success", "message": "已启动强制刷新任务，这可能需要一些时间"}

# 添加强制刷新随机推荐的接口
@app.post("/api/recommendations/random/force-refresh")
def force_refresh_random_recommendations(
    background_tasks: BackgroundTasks, 
    category: Optional[str] = None,
    limit: int = 10, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """强制刷新随机推荐论文（不使用缓存），可以按照领域过滤"""
    try:
        # 清除缓存并重新获取数据
        # 强制刷新特定领域的期刊数据
        if category:
            journals = db.query(Journal).filter(Journal.category == category).all()
            for journal in journals:
                background_tasks.add_task(journal_service.force_refresh_latest_papers, db, limit, [journal.id])
            
        random_recommendations = recommendation_service.get_random_recommendations(
            db=db, 
            user_id=current_user.id, 
            category=category, 
            limit=limit,
            force_refresh=True  # 添加强制刷新标记
        )
        
        # 返回格式改为与普通随机推荐接口一致
        return {"recommendations": random_recommendations}
    except Exception as e:
        logger.error(f"强制刷新随机推荐论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"强制刷新随机推荐论文失败: {str(e)}")

# 推荐相关路由
@app.get("/api/recommendations")
def get_recommendations(limit: int = 10, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """获取当前用户的推荐论文"""
    try:
        recommendations = recommendation_service.get_user_recommendations(db, current_user.id, limit)
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"获取推荐论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取推荐论文失败")

@app.post("/api/recommendations/refresh")
def refresh_recommendations(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """刷新用户推荐"""
    background_tasks.add_task(recommendation_service.refresh_recommendations, db, current_user.id)
    return {"status": "success", "message": "推荐刷新任务已启动"}

@app.post("/api/recommendations/force-refresh")
def force_refresh_recommendations(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """强制刷新用户推荐（不使用缓存）"""
    # 首先清除用户的所有推荐
    db.query(Recommendation).filter(Recommendation.user_id == current_user.id).delete()
    db.commit()
    
    # 然后重新生成推荐
    background_tasks.add_task(recommendation_service.generate_recommendations, db, current_user.id)
    return {"status": "success", "message": "已启动强制刷新推荐任务，这可能需要一些时间"}

# 用户活动历史
@app.get("/api/user-activities")
async def get_user_activities(
    limit: int = Query(20, ge=1, le=100),
    action_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取用户活动历史"""
    activities = await history_service.get_user_history(
        user_id=current_user.id,
        action_type=action_type,
        limit=limit
    )
    return activities

# 简单的健康检查端点
@app.get("/api/ping")
async def ping():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# 添加全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    logger.error(f"请求验证异常: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "detail": "请求数据验证失败",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    # 记录错误详情用于调试
    error_details = traceback.format_exc()
    logger.error(f"服务器异常: {str(exc)}")
    logger.error(f"详细错误: {error_details}")
    
    # 对于登录相关错误，提供更友好的消息
    if "登录" in request.url.path or "token" in request.url.path:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "detail": "登录服务暂时不可用，请稍后重试",
                "debug_info": str(exc) if settings.DEBUG else None
            }
        )
    
    # 常规错误处理
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "detail": "服务器内部错误，请稍后重试",
            "message": str(exc) if settings.DEBUG else "服务器内部错误"
        }
    )

@app.post("/api/graph/batch-extract-concepts")
async def batch_extract_concepts(
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量从论文中提取概念并构建知识图谱，代理到知识图谱路由"""
    # 转发到知识图谱路由处理函数
    from .routers.knowledge_graph import batch_extract_concepts as route_batch_extract
    return await route_batch_extract(db=db, current_user=current_user, limit=limit)

@app.get("/api/graph/reading-path/{concept_id}")
async def get_reading_path(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学习路径，代理到知识图谱路由"""
    # 转发到知识图谱路由处理函数
    from .routers.knowledge_graph import get_reading_path as route_get_reading_path
    return await route_get_reading_path(concept_id=concept_id, db=db, current_user=current_user)

@app.delete("/api/graph/concept/{concept_id}")
async def delete_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除概念，代理到知识图谱路由"""
    # 转发到知识图谱路由处理函数
    from .routers.knowledge_graph import delete_concept as route_delete_concept
    return await route_delete_concept(concept_id=concept_id, db=db, current_user=current_user)

@app.get("/api/graph/concept/{concept_id}")
async def get_concept_detail(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取概念详情，代理到知识图谱路由"""
    # 转发到知识图谱路由处理函数
    from .routers.knowledge_graph import get_concept_detail as route_get_concept_detail
    return await route_get_concept_detail(concept_id=concept_id, db=db, current_user=current_user)

@app.put("/api/graph/concept/{concept_id}")
async def update_concept(
    concept_id: int,
    concept_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新概念，代理到知识图谱路由"""
    # 转发到知识图谱路由处理函数
    from .routers.knowledge_graph import update_concept as route_update_concept
    from app.schemas.knowledge_graph import ConceptUpdate
    concept_update = ConceptUpdate(**concept_data)
    return await route_update_concept(concept_id=concept_id, concept_data=concept_update, db=db, current_user=current_user)

@app.delete("/api/graph/relation/{relation_id}")
async def delete_relation(
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除概念关系，代理到知识图谱路由"""
    # 转发到知识图谱路由处理函数
    from .routers.knowledge_graph import delete_relation as route_delete_relation
    return await route_delete_relation(relation_id=relation_id, db=db, current_user=current_user)

@app.post("/api/graph/extract-concepts/{paper_id}")
async def extract_concepts_from_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从论文中提取概念，代理到知识图谱路由"""
    # 转发到知识图谱路由处理函数
    from .routers.knowledge_graph import extract_concepts_from_paper as route_extract_concepts
    return await route_extract_concepts(paper_id=paper_id, db=db, current_user=current_user)

@app.post("/api/papers/{paper_id}/upload-pdf", response_model=dict)
async def upload_paper_pdf(
    paper_id: int,
    pdf_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为已存在的论文上传PDF文件"""
    try:
        # 确保用户对象有storage_used和storage_capacity属性
        if not hasattr(current_user, 'storage_used') or current_user.storage_used is None:
            current_user.storage_used = 0
            db.commit()
            
        if not hasattr(current_user, 'storage_capacity') or current_user.storage_capacity is None:
            current_user.storage_capacity = 500  # 默认500MB
            db.commit()
            
        # 先检查论文是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            logger.error(f"论文ID {paper_id} 不存在")
            raise HTTPException(status_code=404, detail=f"论文ID {paper_id} 不存在")
            
        # 再检查权限
        if paper.user_id != current_user.id:
            logger.error(f"用户 {current_user.id} 无权访问论文 {paper_id}")
            raise HTTPException(status_code=403, detail=f"无权访问此论文，该论文属于用户ID {paper.user_id}")
        
        # 如果已有PDF，先删除旧文件释放空间
        if paper.local_pdf_path and os.path.exists(paper.local_pdf_path):
            try:
                file_size = os.path.getsize(paper.local_pdf_path)
                os.remove(paper.local_pdf_path)
                current_user.storage_used = max(0, current_user.storage_used - file_size / (1024 * 1024))
            except Exception as e:
                logger.error(f"删除旧PDF文件失败: {str(e)}")
                # 继续处理，不中断上传
        
        # 检查存储容量
        file_content = await pdf_file.read()
        file_size_mb = len(file_content) / (1024 * 1024)  # 转换为MB
        
        if current_user.storage_used + file_size_mb > current_user.storage_capacity:
            raise HTTPException(status_code=400, detail="存储空间不足")
        
        # 创建用户的论文目录
        os.makedirs(os.path.join(UPLOAD_DIR, f"user_{current_user.id}", "papers"), exist_ok=True)
        
        # 构建文件路径
        file_name = f"{paper_id}_{uuid.uuid4()}.pdf"
        file_path = os.path.join(UPLOAD_DIR, f"user_{current_user.id}", "papers", file_name)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 更新论文记录和用户存储使用量
        paper.local_pdf_path = file_path
        paper.has_pdf = True
        current_user.storage_used += file_size_mb
        
        db.commit()
        
        return {
            "success": True,
            "message": "PDF上传成功",
            "file_path": file_path,
            "file_size_mb": file_size_mb
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传PDF文件失败: {str(e)}")
        logger.exception("详细错误信息")
        raise HTTPException(status_code=500, detail=f"上传PDF文件失败: {str(e)}")

# Sci-Hub相关接口
@app.get("/api/scihub/download")
async def download_paper_from_scihub(doi: str):
    """
    从Sci-Hub下载论文，返回可下载的URL
    """
    try:
        paper_info = scihub_service.get_paper_by_doi(doi)
        if not paper_info or not paper_info.get("pdf_url"):
            raise HTTPException(status_code=404, detail="无法找到该DOI对应的论文PDF")
        
        return {"url": paper_info.get("pdf_url"), "title": paper_info.get("title")}
    except Exception as e:
        logging.error(f"从Sci-Hub下载PDF失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

@app.get("/api/scihub/pdf")
async def get_pdf_from_scihub(doi: str):
    """
    从Sci-Hub获取PDF并直接返回PDF文件，避免前端CORS限制
    """
    try:
        paper_info = scihub_service.get_paper_by_doi(doi)
        if not paper_info or not paper_info.get("pdf_url"):
            raise HTTPException(status_code=404, detail="无法找到该DOI对应的论文PDF")
        
        pdf_url = paper_info.get("pdf_url")
        pdf_content = scihub_service.download_pdf(pdf_url)
        
        if not pdf_content:
            raise HTTPException(status_code=404, detail="PDF下载失败")
        
        # 返回PDF文件流
        filename = f"{doi.replace('/', '_')}.pdf"
        
        # 返回流式响应
        return StreamingResponse(
            iter([pdf_content]), 
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logging.error(f"从Sci-Hub获取PDF失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取PDF失败: {str(e)}")

@app.get("/api/scihub/mirrors")
async def get_available_scihub_mirrors():
    """获取可用的Sci-Hub镜像站点列表"""
    try:
        domains = scihub_service.get_available_domains()
        return {"mirrors": domains}
    except Exception as e:
        logging.error(f"获取Sci-Hub镜像列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取镜像列表失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    ) 
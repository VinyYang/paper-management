from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies import get_db, get_current_user
from ..models import User, Paper as PaperModel, Concept, paper_concepts, ConceptRelation
from ..schemas.graph import (
    ConceptNode,
    ConceptEdge,
    GraphResponse,
    ConceptDetail,
    ConceptRelationCreate,
    ConceptRelationUpdate
)
from ..schemas.paper import Paper
from sqlalchemy import func
import logging

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.get("/concepts/", response_model=List[ConceptNode])
async def get_concepts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取概念列表"""
    try:
        concepts = db.query(Concept).offset(skip).limit(limit).all()
        return concepts
    except Exception as e:
        logger.error(f"获取概念列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取概念列表失败: {str(e)}")

@router.get("/concepts/{concept_id}", response_model=ConceptDetail)
async def get_concept_detail(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取概念详情"""
    try:
        concept = db.query(Concept).filter(Concept.id == concept_id).first()
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="概念不存在"
            )
        
        # 获取相关论文
        papers = db.query(PaperModel).join(paper_concepts).filter(
            paper_concepts.concept_id == concept_id
        ).all()
        
        # 获取相关概念
        related_concepts = db.query(Concept).join(ConceptRelation).filter(
            (ConceptRelation.source_id == concept_id) |
            (ConceptRelation.target_id == concept_id)
        ).all()
        
        return {
            "concept": concept,
            "papers": papers,
            "related_concepts": related_concepts
        }
    except Exception as e:
        logger.error(f"获取概念详情失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取概念详情失败: {str(e)}")

@router.get("/relations/", response_model=List[ConceptEdge])
async def get_concept_relations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取概念关系列表"""
    try:
        relations = db.query(ConceptRelation).offset(skip).limit(limit).all()
        return relations
    except Exception as e:
        logger.error(f"获取概念关系列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取概念关系列表失败: {str(e)}")

@router.post("/relations/", response_model=ConceptEdge)
async def create_concept_relation(
    relation_data: ConceptRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建概念关系"""
    try:
        # 检查概念是否存在
        source = db.query(Concept).filter(Concept.id == relation_data.source_id).first()
        target = db.query(Concept).filter(Concept.id == relation_data.target_id).first()
        
        if not source or not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="源概念或目标概念不存在"
            )
        
        # 创建关系
        relation = ConceptRelation(
            source_id=relation_data.source_id,
            target_id=relation_data.target_id,
            relation_type=relation_data.relation_type,
            weight=relation_data.weight,
            description=relation_data.description
        )
        
        db.add(relation)
        db.commit()
        db.refresh(relation)
        
        return relation
    except Exception as e:
        db.rollback()
        logger.error(f"创建概念关系失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"创建概念关系失败: {str(e)}")

@router.put("/relations/{relation_id}", response_model=ConceptEdge)
async def update_concept_relation(
    relation_id: int,
    relation_data: ConceptRelationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新概念关系"""
    try:
        relation = db.query(ConceptRelation).filter(ConceptRelation.id == relation_id).first()
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="概念关系不存在"
            )
        
        # 更新字段
        for key, value in relation_data.dict(exclude_unset=True).items():
            setattr(relation, key, value)
        
        db.commit()
        db.refresh(relation)
        
        return relation
    except Exception as e:
        db.rollback()
        logger.error(f"更新概念关系失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"更新概念关系失败: {str(e)}")

@router.delete("/relations/{relation_id}")
async def delete_concept_relation(
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除概念关系"""
    try:
        relation = db.query(ConceptRelation).filter(ConceptRelation.id == relation_id).first()
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="概念关系不存在"
            )
        
        db.delete(relation)
        db.commit()
        
        return {"message": "概念关系已成功删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除概念关系失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除概念关系失败: {str(e)}")

@router.get("/visualization/", response_model=GraphResponse)
async def get_graph_visualization(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识图谱可视化数据"""
    try:
        # 获取节点（概念）
        nodes = db.query(Concept).limit(limit).all()
        
        # 获取边（关系）
        edges = db.query(ConceptRelation).filter(
            (ConceptRelation.source_id.in_([node.id for node in nodes])) &
            (ConceptRelation.target_id.in_([node.id for node in nodes]))
        ).all()
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    except Exception as e:
        logger.error(f"获取知识图谱可视化数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取知识图谱可视化数据失败: {str(e)}")

@router.get("/concepts/{concept_id}/papers/", response_model=List[Paper])
async def get_concept_papers(
    concept_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取概念相关的论文"""
    try:
        papers = db.query(PaperModel).join(paper_concepts).filter(
            paper_concepts.concept_id == concept_id
        ).offset(skip).limit(limit).all()
        
        return papers
    except Exception as e:
        logger.error(f"获取概念相关论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取概念相关论文失败: {str(e)}")

@router.get("/concepts/{concept_id}/related/", response_model=List[ConceptNode])
async def get_related_concepts(
    concept_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取相关概念"""
    try:
        # 获取直接相关的概念
        related_concepts = db.query(Concept).join(ConceptRelation).filter(
            (ConceptRelation.source_id == concept_id) |
            (ConceptRelation.target_id == concept_id)
        ).limit(limit).all()
        
        return related_concepts
    except Exception as e:
        logger.error(f"获取相关概念失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取相关概念失败: {str(e)}") 
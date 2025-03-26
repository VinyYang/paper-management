from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, Form, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional, Set
import logging
from collections import Counter
import re
import networkx as nx
from itertools import combinations
from pydantic import BaseModel

from ..dependencies import get_db, get_current_user
from ..models import User, Concept, ConceptRelation, Paper, paper_concepts
from ..schemas.knowledge_graph import (
    ConceptCreate, 
    ConceptUpdate, 
    Concept as ConceptSchema,
    ConceptRelationCreate,
    ConceptRelation as ConceptRelationSchema,
    Graph,
    PaperSimilarity,
    DetailedSimilarity
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/concepts/", response_model=ConceptSchema)
async def create_concept(
    concept_data: ConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查概念名称是否已存在
    existing_concept = db.query(Concept).filter(Concept.name == concept_data.name).first()
    if existing_concept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="概念名称已存在"
        )
    
    # 创建新概念
    concept = Concept(
        name=concept_data.name,
        description=concept_data.description,
        category=concept_data.category if concept_data.category is not None else 0
    )
    
    db.add(concept)
    db.commit()
    db.refresh(concept)
    
    return concept

@router.get("/concepts/", response_model=List[ConceptSchema])
async def get_concepts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        concepts = db.query(Concept).offset(skip).limit(limit).all()
        return concepts
    except Exception as e:
        logger.error(f"获取概念失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取概念失败: {e}"
        )

@router.get("/concepts/{concept_id}", response_model=ConceptSchema)
async def get_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="概念不存在"
        )
    
    return concept

@router.post("/relations/", response_model=ConceptRelationSchema)
async def create_relation(
    relation_data: ConceptRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查源概念和目标概念是否存在
    source_concept = db.query(Concept).filter(Concept.id == relation_data.source_id).first()
    target_concept = db.query(Concept).filter(Concept.id == relation_data.target_id).first()
    
    if not source_concept or not target_concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="源概念或目标概念不存在"
        )
    
    # 检查是否已经存在相同的关系
    existing_relation = db.query(ConceptRelation).filter(
        ConceptRelation.source_id == relation_data.source_id,
        ConceptRelation.target_id == relation_data.target_id,
        ConceptRelation.relation_type == relation_data.relation_type
    ).first()
    
    if existing_relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关系已经存在"
        )
    
    # 创建新关系
    relation = ConceptRelation(
        source_id=relation_data.source_id,
        target_id=relation_data.target_id,
        relation_type=relation_data.relation_type,
        weight=relation_data.weight
    )
    
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation

@router.get("/knowledge-graph")
def get_graph(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 获取所有概念和关系，手动指定要查询的列
        concepts = db.query(
            Concept.id, 
            Concept.name, 
            Concept.description, 
            Concept.created_at, 
            Concept.updated_at
        ).all()
        
        relations = db.query(ConceptRelation).all()
        
        # 获取每个概念相关的论文数量，用于设置节点大小
        concept_papers_count = {}
        for concept in concepts:
            paper_count = db.query(func.count(paper_concepts.c.paper_id)).filter(
                paper_concepts.c.concept_id == concept.id
            ).scalar() or 0
            concept_papers_count[concept.id] = paper_count
        
        # 构建图数据
        nodes = [
            {
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                # 根据权重和相关论文数量动态设置节点大小
                "symbolSize": max(30, min(80, 40 + (concept_papers_count[c.id] * 5))),
                # 为所有概念默认设置类别为0
                "category": 0,
                # 添加更多元数据用于前端交互和展示
                "weight": 1.0, # 默认权重
                "paperCount": concept_papers_count[c.id],
                "createdAt": c.created_at.isoformat() if hasattr(c, 'created_at') else None,
                "updatedAt": c.updated_at.isoformat() if hasattr(c, 'updated_at') else None
            }
            for c in concepts
        ]
        
        # 链接分组以避免重复连接视觉混乱
        # 创建连接分组字典，记录相同源目标节点之间的不同类型关系
        link_groups = {}
        for r in relations:
            key = f"{r.source_id}-{r.target_id}"
            if key not in link_groups:
                link_groups[key] = {
                    "source": str(r.source_id),
                    "target": str(r.target_id),
                    "relations": [],
                    "total_weight": 0
                }
            # 添加关系类型和权重
            link_groups[key]["relations"].append({
                "id": r.id,
                "type": r.relation_type,
                "weight": r.weight or 1.0
            })
            link_groups[key]["total_weight"] += (r.weight or 1.0)
        
        # 创建可视化友好的链接
        links = []
        for key, group in link_groups.items():
            # 为每一组关系创建一个链接
            relation_labels = [r["type"] for r in group["relations"]]
            links.append({
                "source": group["source"],
                "target": group["target"],
                "value": group["total_weight"],
                "label": ", ".join(relation_labels),
                "relations": group["relations"]
            })
        
        # 定义概念类别
        categories = [
            {"name": "概念", "itemStyle": {"color": "#5470c6"}},
            {"name": "方法", "itemStyle": {"color": "#91cc75"}},
            {"name": "工具", "itemStyle": {"color": "#fac858"}},
            {"name": "应用", "itemStyle": {"color": "#ee6666"}},
            {"name": "领域", "itemStyle": {"color": "#73c0de"}},
            {"name": "其他", "itemStyle": {"color": "#3ba272"}}
        ]
        
        # 返回图数据
        return {
            "nodes": nodes,
            "links": links,
            "categories": categories,
            "stats": {
                "conceptCount": len(nodes),
                "relationCount": len(links)
            }
        }
        
    except Exception as e:
        logger.error(f"获取知识图谱数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识图谱数据失败: {e}"
        )

@router.put("/concepts/{concept_id}/weight", response_model=ConceptSchema)
async def update_concept_weight(
    concept_id: int,
    weight: float = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 手动指定要查询的列，不包括category
    concept = db.query(
        Concept.id, 
        Concept.name, 
        Concept.description, 
        Concept.created_at, 
        Concept.updated_at
    ).filter(Concept.id == concept_id).first()
    
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="概念不存在"
        )
    
    # 获取原模型进行更新
    original_concept = db.query(Concept).filter(Concept.id == concept_id).first()
    
    # 更新概念权重
    original_concept.weight = weight
    
    db.commit()
    db.refresh(original_concept)
    
    # 返回时添加默认category
    result = {
        "id": original_concept.id,
        "name": original_concept.name,
        "description": original_concept.description,
        "category": 0,  # 默认类别
        "created_at": original_concept.created_at,
        "updated_at": original_concept.updated_at
    }
    
    return result

@router.put("/relations/{relation_id}/weight", response_model=ConceptRelationSchema)
async def update_relation_weight(
    relation_id: int,
    weight: float = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    relation = db.query(ConceptRelation).filter(ConceptRelation.id == relation_id).first()
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关系不存在"
        )
    
    # 更新关系权重
    relation.weight = weight
    
    db.commit()
    db.refresh(relation)
    return relation

@router.get("/concept-papers/{concept_id}")
async def get_papers_by_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取与概念相关的论文"""
    # 检查概念是否存在，只查询ID
    concept_exists = db.query(Concept.id).filter(Concept.id == concept_id).scalar()
    if not concept_exists:
        raise HTTPException(status_code=404, detail="概念不存在")
    
    # 使用SQL联接查询与概念相关的论文
    try:
        papers = (
            db.query(Paper)
            .join(paper_concepts, Paper.id == paper_concepts.c.paper_id)
            .filter(
                paper_concepts.c.concept_id == concept_id,
                Paper.user_id == current_user.id
            )
            .all()
        )
        
        return papers
    except Exception as e:
        logger.error(f"获取概念相关论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取概念相关论文失败: {str(e)}")

# 新添加的功能：从论文中提取关键概念
@router.post("/extract-concepts/{paper_id}")
async def extract_concepts_from_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从论文标题和摘要中提取关键概念并添加到知识图谱中"""
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在或无权访问")
        
    if not paper.abstract or paper.abstract.strip() == "":
        raise HTTPException(status_code=400, detail="论文没有摘要，无法提取概念")
    
    # 改进的关键词提取算法
    text = f"{paper.title} {paper.abstract}"
    
    # 使用预定义的停用词和正则表达式过滤常见单词
    stop_words = {
        "the", "a", "an", "and", "or", "but", "if", "then", "of", "at", "to", "for", "with", "by", 
        "in", "on", "is", "are", "was", "were", "be", "this", "that", "have", "has", "had",
        "do", "does", "did", "can", "could", "will", "would", "shall", "should", "may", "might",
        "i", "you", "he", "she", "it", "we", "they", "their", "our", "my", "your", "his", "her",
        "its", "there", "here", "where", "when", "why", "how", "what", "who", "which", "such",
        "some", "any", "all", "many", "much", "more", "most", "other", "another", "each", "every"
    }
    
    # 提取单词和短语
    # 先尝试提取2-3个词的短语
    phrases = re.findall(r'\b[a-zA-Z][a-zA-Z\-]{2,}\s+(?:[a-zA-Z][a-zA-Z\-]{2,}\s+){0,2}[a-zA-Z][a-zA-Z\-]{2,}\b', text.lower())
    
    # 提取单个重要术语
    words = re.findall(r'\b[a-zA-Z][a-zA-Z\-]{2,}\b', text.lower())
    
    # 过滤停用词
    filtered_words = [word for word in words if word not in stop_words]
    filtered_phrases = []
    
    for phrase in phrases:
        parts = phrase.split()
        # 如果短语中所有单词都不是停用词
        if all(part not in stop_words for part in parts):
            filtered_phrases.append(phrase)
    
    # 组合短语和单词
    all_concepts = filtered_phrases + filtered_words
    
    # 计算词频
    concept_counts = Counter(all_concepts)
    
    # 选择频率较高的概念（至少出现1次）
    # 优先选择短语，因为短语通常更有意义
    top_phrases = [phrase for phrase, count in concept_counts.most_common(20) if len(phrase.split()) > 1 and count >= 1]
    top_single_words = [word for word, count in concept_counts.most_common(20) if len(word.split()) == 1 and count >= 2]
    
    # 限制概念总数量
    top_concepts = top_phrases[:10] + top_single_words[:10] 
    
    # 如果没有提取到任何概念，尝试使用文章标题作为概念
    if not top_concepts and paper.title:
        title_parts = paper.title.lower().split()
        title_parts = [part for part in title_parts if part not in stop_words and len(part) > 3]
        if title_parts:
            top_concepts = [' '.join(title_parts[:3]) if len(title_parts) > 2 else ' '.join(title_parts)]
    
    # 如果还是没有概念，返回错误
    if not top_concepts:
        raise HTTPException(status_code=400, detail="无法从论文中提取有效概念，请手动添加")
    
    # 创建概念并与论文关联
    created_concepts = []
    for concept_name in top_concepts:
        # 检查概念是否已存在
        concept = db.query(Concept).filter(Concept.name == concept_name).first()
        if not concept:
            # 创建新概念
            concept = Concept(name=concept_name)
            db.add(concept)
            db.flush()  # 获取ID但不提交事务
        
        # 将概念与论文关联（如果尚未关联）
        existing_relation = db.query(paper_concepts).filter(
            paper_concepts.c.paper_id == paper.id,
            paper_concepts.c.concept_id == concept.id
        ).first()
        
        if not existing_relation:
            # 添加关联
            stmt = paper_concepts.insert().values(paper_id=paper.id, concept_id=concept.id)
            db.execute(stmt)
        
        created_concepts.append({"id": concept.id, "name": concept.name})
    
    # 尝试推断概念之间的关系（简单实现，可以用更复杂的算法改进）
    # 这里假设共同出现在同一篇论文的概念之间可能存在关系
    for concept1, concept2 in combinations(created_concepts, 2):
        # 检查关系是否已存在
        existing_relation = db.query(ConceptRelation).filter(
            or_(
                and_(
                    ConceptRelation.source_id == concept1["id"],
                    ConceptRelation.target_id == concept2["id"]
                ),
                and_(
                    ConceptRelation.source_id == concept2["id"],
                    ConceptRelation.target_id == concept1["id"]
                )
            )
        ).first()
        
        if not existing_relation:
            # 创建新关系，关系类型为"相关"
            relation = ConceptRelation(
                source_id=concept1["id"],
                target_id=concept2["id"],
                relation_type="相关"
            )
            db.add(relation)
    
    db.commit()
    
    return {
        "paper_id": paper.id,
        "title": paper.title,
        "extracted_concepts": created_concepts
    }

# 新添加的功能：批量从论文中提取概念
@router.post("/batch-extract-concepts")
async def batch_extract_concepts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, description="要处理的论文数量限制")
):
    """批量从论文中提取概念并构建知识图谱"""
    # 获取用户的论文，优先处理有摘要的论文
    papers = (
        db.query(Paper)
        .filter(Paper.user_id == current_user.id)
        .filter(Paper.abstract != None)
        .filter(Paper.abstract != "")
        .limit(limit)
        .all()
    )
    
    if not papers:
        return {
            "processed_count": 0,
            "details": [],
            "message": "没有找到可处理的论文，请确保论文有摘要"
        }
    
    results = []
    for paper in papers:
        try:
            # 使用与单个论文相同的提取逻辑
            text = f"{paper.title} {paper.abstract}"
            
            # 使用预定义的停用词
            stop_words = {
                "the", "a", "an", "and", "or", "but", "if", "then", "of", "at", "to", "for", "with", "by", 
                "in", "on", "is", "are", "was", "were", "be", "this", "that", "have", "has", "had",
                "do", "does", "did", "can", "could", "will", "would", "shall", "should", "may", "might",
                "i", "you", "he", "she", "it", "we", "they", "their", "our", "my", "your", "his", "her",
                "its", "there", "here", "where", "when", "why", "how", "what", "who", "which", "such",
                "some", "any", "all", "many", "much", "more", "most", "other", "another", "each", "every"
            }
            
            # 提取短语和单词
            phrases = re.findall(r'\b[a-zA-Z][a-zA-Z\-]{2,}\s+(?:[a-zA-Z][a-zA-Z\-]{2,}\s+){0,2}[a-zA-Z][a-zA-Z\-]{2,}\b', text.lower())
            words = re.findall(r'\b[a-zA-Z][a-zA-Z\-]{2,}\b', text.lower())
            
            # 过滤
            filtered_words = [word for word in words if word not in stop_words]
            filtered_phrases = []
            
            for phrase in phrases:
                parts = phrase.split()
                if all(part not in stop_words for part in parts):
                    filtered_phrases.append(phrase)
            
            # 组合和计数
            all_concepts = filtered_phrases + filtered_words
            concept_counts = Counter(all_concepts)
            
            # 选择最佳概念
            top_phrases = [phrase for phrase, count in concept_counts.most_common(20) if len(phrase.split()) > 1 and count >= 1]
            top_single_words = [word for word, count in concept_counts.most_common(20) if len(word.split()) == 1 and count >= 2]
            
            # 限制概念总数
            top_concepts = top_phrases[:10] + top_single_words[:10]
            
            # 如果没有提取到概念，尝试使用标题
            if not top_concepts and paper.title:
                title_parts = paper.title.lower().split()
                title_parts = [part for part in title_parts if part not in stop_words and len(part) > 3]
                if title_parts:
                    top_concepts = [' '.join(title_parts[:3]) if len(title_parts) > 2 else ' '.join(title_parts)]
            
            # 如果没有有效概念，跳过这篇论文
            if not top_concepts:
                logger.warning(f"无法从论文 ID:{paper.id} '{paper.title}' 中提取有效概念")
                continue
            
            created_concepts = []
            for concept_name in top_concepts:
                concept = db.query(Concept).filter(Concept.name == concept_name).first()
                if not concept:
                    concept = Concept(name=concept_name)
                    db.add(concept)
                    db.flush()
                
                existing_relation = db.query(paper_concepts).filter(
                    paper_concepts.c.paper_id == paper.id,
                    paper_concepts.c.concept_id == concept.id
                ).first()
                
                if not existing_relation:
                    stmt = paper_concepts.insert().values(paper_id=paper.id, concept_id=concept.id)
                    db.execute(stmt)
                
                created_concepts.append({"id": concept.id, "name": concept.name})
            
            # 建立概念间关系
            for concept1, concept2 in combinations(created_concepts, 2):
                existing_relation = db.query(ConceptRelation).filter(
                    or_(
                        and_(
                            ConceptRelation.source_id == concept1["id"],
                            ConceptRelation.target_id == concept2["id"]
                        ),
                        and_(
                            ConceptRelation.source_id == concept2["id"],
                            ConceptRelation.target_id == concept1["id"]
                        )
                    )
                ).first()
                
                if not existing_relation:
                    relation = ConceptRelation(
                        source_id=concept1["id"],
                        target_id=concept2["id"],
                        relation_type="相关"
                    )
                    db.add(relation)
            
            results.append({
                "paper_id": paper.id,
                "title": paper.title,
                "extracted_concepts": created_concepts
            })
        except Exception as e:
            logger.error(f"处理论文 {paper.id} 时出错: {str(e)}")
    
    db.commit()
    return {
        "processed_count": len(results),
        "details": results,
        "message": f"成功处理了 {len(results)} 篇论文"
    }

# 辅助函数：计算文本相似度（使用Levenshtein距离归一化版本）
def calculate_text_similarity(text1: str, text2: str) -> float:
    """计算两个文本字符串之间的相似度"""
    if not text1 or not text2:
        return 0.0
    
    # 转换为小写以忽略大小写
    s1 = text1.lower()
    s2 = text2.lower()
    
    # 如果字符串完全相同，返回1
    if s1 == s2:
        return 1.0
    
    # 计算Levenshtein距离
    def levenshtein_distance(str1, str2):
        m, n = len(str1), len(str2)
        # 创建距离矩阵
        dp = [[0 for _ in range(n+1)] for _ in range(m+1)]
        
        # 初始化第一行和第一列
        for i in range(m+1):
            dp[i][0] = i
        for j in range(n+1):
            dp[0][j] = j
        
        # 填充距离矩阵
        for i in range(1, m+1):
            for j in range(1, n+1):
                cost = 0 if str1[i-1] == str2[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # 删除
                    dp[i][j-1] + 1,      # 插入
                    dp[i-1][j-1] + cost  # 替换或匹配
                )
        
        return dp[m][n]
    
    # 计算归一化相似度 (1 - normalized_distance)
    distance = levenshtein_distance(s1, s2)
    max_length = max(len(s1), len(s2))
    return 1 - (distance / max_length) if max_length > 0 else 0

# 辅助函数：计算作者相似度
def calculate_author_similarity(authors1: str, authors2: str) -> float:
    """计算两篇论文作者列表的相似度"""
    if not authors1 or not authors2:
        return 0.0
    
    # 分割作者字符串并移除空白
    authors1_list = [a.strip() for a in authors1.split(',') if a.strip()]
    authors2_list = [a.strip() for a in authors2.split(',') if a.strip()]
    
    if not authors1_list or not authors2_list:
        return 0.0
    
    # 找出共同作者
    common_authors = set(authors1_list).intersection(set(authors2_list))
    
    # 计算Jaccard相似度: 交集大小 / 并集大小
    return len(common_authors) / len(set(authors1_list).union(set(authors2_list)))

# 辅助函数：计算年份相近度
def calculate_year_similarity(year1: Optional[int], year2: Optional[int]) -> float:
    """计算两篇论文发表年份的相近度"""
    if year1 is None or year2 is None:
        return 0.0
    
    # 年份差异
    year_diff = abs(year1 - year2)
    
    # 使用指数衰减函数：10年以上的论文相似度接近0
    return max(0, 1 - (year_diff / 10))

# 辅助函数：计算期刊/会议相似度
def calculate_venue_similarity(venue1: Optional[str], venue2: Optional[str]) -> float:
    """计算两篇论文发表期刊/会议的相似度"""
    if not venue1 or not venue2:
        return 0.0
    
    # 转换为字符串确保安全比较
    venue1_str = str(venue1).strip()
    venue2_str = str(venue2).strip()
    
    # 如果字符串为空，返回0
    if not venue1_str or not venue2_str:
        return 0.0
    
    # 如果完全相同返回1.0
    if venue1_str.lower() == venue2_str.lower():
        return 1.0
    
    # 简单的文本相似度
    return calculate_text_similarity(venue1_str, venue2_str)

# 计算两篇论文的综合相似度
def calculate_comprehensive_similarity(
    paper1: Paper,
    paper2: Paper,
    paper1_concept_ids: set,
    paper2_concept_ids: set,
    shared_concepts_count: int,
    weights: Dict[str, float] = None
) -> float:
    """
    计算两篇论文的综合相似度
    
    参数:
    - paper1, paper2: 两篇论文对象
    - paper1_concept_ids, paper2_concept_ids: 两篇论文的概念ID集合
    - shared_concepts_count: 共享概念数量
    - weights: 各维度权重字典，默认为None
    
    返回:
    - 综合相似度值 (0-1)
    """
    # 默认权重配置
    default_weights = {
        "concept": 0.5,    # 概念相似度权重
        "title": 0.2,      # 标题相似度权重
        "author": 0.15,    # 作者相似度权重
        "venue": 0.1,      # 期刊/会议相似度权重
        "year": 0.05       # 年份相近度权重
    }
    
    # 使用提供的权重或默认权重
    if weights is None:
        weights = default_weights
    
    # 1. 计算概念相似度 (Jaccard系数)
    concept_union = len(paper1_concept_ids.union(paper2_concept_ids))
    concept_similarity = shared_concepts_count / concept_union if concept_union > 0 else 0
    
    # 2. 计算标题相似度
    title_similarity = calculate_text_similarity(paper1.title, paper2.title)
    
    # 3. 计算作者相似度
    author_similarity = calculate_author_similarity(paper1.authors, paper2.authors)
    
    # 4. 计算期刊/会议相似度
    # 整合论文的venue和journal字段，确保非空比较
    paper1_venue = paper1.venue if paper1.venue else paper1.journal
    paper2_venue = paper2.venue if paper2.venue else paper2.journal
    venue_similarity = calculate_venue_similarity(paper1_venue, paper2_venue)
    
    # 5. 计算年份相近度
    year_similarity = calculate_year_similarity(paper1.year, paper2.year)
    
    # 计算加权综合相似度
    comprehensive_similarity = (
        weights["concept"] * concept_similarity +
        weights["title"] * title_similarity +
        weights["author"] * author_similarity +
        weights["venue"] * venue_similarity +
        weights["year"] * year_similarity
    )
    
    return comprehensive_similarity

# 新添加的功能：计算论文相似度
@router.post("/paper-similarity", response_model=List[PaperSimilarity])
async def calculate_paper_similarity(
    paper_id: int = Query(..., description="要计算相似度的论文ID"),
    threshold: float = Query(0.3, ge=0, le=1, description="相似度阈值"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """基于综合因素计算论文之间的相似度"""
    # 检查论文是否存在
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在或无权访问")
    
    # 获取该论文的概念
    paper_concepts_query = (
        db.query(Concept.id)
        .join(paper_concepts, Concept.id == paper_concepts.c.concept_id)
        .filter(paper_concepts.c.paper_id == paper_id)
        .all()
    )
    
    paper_concept_ids = {concept.id for concept in paper_concepts_query}
    if not paper_concept_ids:
        # 如果论文没有关联概念，先尝试提取
        await extract_concepts_from_paper(paper_id, db, current_user)
        
        # 重新查询概念
        paper_concepts_query = (
            db.query(Concept.id)
            .join(paper_concepts, Concept.id == paper_concepts.c.concept_id)
            .filter(paper_concepts.c.paper_id == paper_id)
            .all()
        )
        paper_concept_ids = {concept.id for concept in paper_concepts_query}
        
        if not paper_concept_ids:
            raise HTTPException(status_code=400, detail="无法从论文中提取概念")
    
    # 查找用户的所有论文，而不仅仅是共享概念的论文
    user_papers_query = (
        db.query(
            Paper.id,
            Paper.title,
            Paper.authors,
            Paper.year,
            Paper.venue,
            Paper.journal
        )
        .filter(
            Paper.id != paper_id,
            Paper.user_id == current_user.id
        )
        .all()
    )
    
    # 计算综合相似度
    similarities = []
    for p in user_papers_query:
        # 获取论文的概念
        other_paper_concepts = (
            db.query(Concept.id)
            .join(paper_concepts, Concept.id == paper_concepts.c.concept_id)
            .filter(paper_concepts.c.paper_id == p.id)
            .all()
        )
        other_concept_ids = {concept.id for concept in other_paper_concepts}
        
        # 计算共享概念数量
        shared_concepts = len(paper_concept_ids.intersection(other_concept_ids))
        
        # 计算各维度相似度
        # 1. 概念相似度 (Jaccard系数)
        concept_union = len(paper_concept_ids.union(other_concept_ids))
        concept_similarity = shared_concepts / concept_union if concept_union > 0 else 0
        
        # 2. 标题相似度
        title_similarity = calculate_text_similarity(paper.title, p.title)
        
        # 3. 作者相似度
        author_similarity = calculate_author_similarity(paper.authors, p.authors)
        
        # 4. 期刊/会议相似度
        paper1_venue = paper.venue if paper.venue else paper.journal
        paper2_venue = p.venue if p.venue else p.journal
        venue_similarity = calculate_venue_similarity(paper1_venue, paper2_venue)
        
        # 5. 年份相近度
        year_similarity = calculate_year_similarity(paper.year, p.year)
        
        # 计算综合相似度
        comprehensive_similarity = calculate_comprehensive_similarity(
            paper, p, paper_concept_ids, {concept.id for concept in other_paper_concepts}, shared_concepts
        )
        
        if comprehensive_similarity >= threshold:
            similarities.append({
                "paper_id": p.id,
                "title": p.title,
                "authors": p.authors,
                "year": p.year,
                "similarity": comprehensive_similarity,
                "shared_concepts": shared_concepts,
                "concept_similarity": concept_similarity,
                "title_similarity": title_similarity,
                "author_similarity": author_similarity,
                "venue_similarity": venue_similarity,
                "year_similarity": year_similarity,
                "source_id": paper_id,
                "target_id": p.id,
                "abstract_similarity": 0.0  # 默认值，如果有计算可以替换
            })
    
    # 按相似度排序并限制结果数量
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities[:limit]

# 新添加的功能：获取推荐阅读路径
@router.get("/reading-path/{concept_id}")
async def get_reading_path(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """基于知识图谱生成推荐学习路径"""
    # 检查概念是否存在
    target_concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not target_concept:
        raise HTTPException(status_code=404, detail="目标概念不存在")
    
    # 获取所有概念和关系，构建图结构
    all_concepts = db.query(Concept).all()
    all_relations = db.query(ConceptRelation).all()
    
    # 构建有向图
    G = nx.DiGraph()
    
    # 添加节点
    for concept in all_concepts:
        G.add_node(concept.id, name=concept.name, description=concept.description)
    
    # 添加边
    for relation in all_relations:
        G.add_edge(
            relation.source_id, 
            relation.target_id, 
            type=relation.relation_type,
            weight=relation.weight or 1.0
        )
    
    # 查找图中的所有根节点（入度为0的节点）
    root_nodes = [node for node, in_degree in G.in_degree() if in_degree == 0]
    
    # 如果没有根节点，选择入度最小的节点作为起点
    if not root_nodes:
        root_nodes = [min(G.nodes(), key=lambda n: G.in_degree(n))]
    
    learning_paths = []
    
    # 从每个根节点尝试找到通往目标概念的路径
    for root in root_nodes:
        try:
            if nx.has_path(G, root, concept_id):
                path = nx.shortest_path(G, root, concept_id, weight='weight')
                
                # 获取路径上的概念详情
                path_concepts = []
                for node_id in path:
                    concept = next((c for c in all_concepts if c.id == node_id), None)
                    if concept:
                        # 查找与该概念相关的论文
                        papers = (
                            db.query(Paper)
                            .join(paper_concepts, Paper.id == paper_concepts.c.paper_id)
                            .filter(
                                paper_concepts.c.concept_id == concept.id,
                                Paper.user_id == current_user.id
                            )
                            .limit(3)
                            .all()
                        )
                        
                        path_concepts.append({
                            "id": concept.id,
                            "name": concept.name,
                            "description": concept.description,
                            "related_papers": [
                                {"id": p.id, "title": p.title, "authors": p.authors}
                                for p in papers
                            ]
                        })
                
                learning_paths.append({
                    "start_concept": G.nodes[root]["name"],
                    "target_concept": target_concept.name,
                    "path_length": len(path) - 1,  # 边的数量
                    "concepts": path_concepts
                })
        except nx.NetworkXNoPath:
            continue
    
    if not learning_paths:
        # 如果没有找到路径，返回仅包含目标概念的单节点路径
        concept_papers = (
            db.query(Paper)
            .join(paper_concepts, Paper.id == paper_concepts.c.paper_id)
            .filter(
                paper_concepts.c.concept_id == concept_id,
                Paper.user_id == current_user.id
            )
            .limit(3)
            .all()
        )
        
        learning_paths.append({
            "start_concept": target_concept.name,
            "target_concept": target_concept.name,
            "path_length": 0,
            "concepts": [{
                "id": target_concept.id,
                "name": target_concept.name,
                "description": target_concept.description,
                "related_papers": [
                    {"id": p.id, "title": p.title, "authors": p.authors}
                    for p in concept_papers
                ]
            }]
        })
    
    return {
        "target_concept": {
            "id": target_concept.id,
            "name": target_concept.name,
            "description": target_concept.description
        },
        "learning_paths": learning_paths
    }

@router.get("/concept/{concept_id}", response_model=ConceptSchema)
async def get_concept_detail(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个概念详情"""
    try:
        concept = db.query(Concept).filter(Concept.id == concept_id).first()
        
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="概念不存在"
            )
        
        return concept
    except Exception as e:
        logger.error(f"获取概念详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取概念详情失败: {e}"
        )

@router.put("/concept/{concept_id}", response_model=ConceptSchema)
async def update_concept(
    concept_id: int,
    concept_data: ConceptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新概念信息"""
    try:
        concept = db.query(Concept).filter(Concept.id == concept_id).first()
        
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="概念不存在"
            )
        
        # 更新字段
        if concept_data.name is not None:
            concept.name = concept_data.name
        if concept_data.description is not None:
            concept.description = concept_data.description
        if concept_data.category is not None:
            concept.category = concept_data.category
        
        # 提交更改
        db.commit()
        db.refresh(concept)
        
        return concept
    except Exception as e:
        logger.error(f"更新概念失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新概念失败: {e}"
        )

@router.delete("/concept/{concept_id}")
async def delete_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除概念"""
    try:
        # 直接查询概念对象
        concept = db.query(Concept).filter(Concept.id == concept_id).first()
        
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="概念不存在"
            )
        
        # 删除与概念相关的所有关系
        db.query(ConceptRelation).filter(
            or_(
                ConceptRelation.source_id == concept_id,
                ConceptRelation.target_id == concept_id
            )
        ).delete(synchronize_session=False)
        
        # 删除概念本身
        db.delete(concept)
        db.commit()
        
        return {"status": "success", "message": "概念已成功删除"}
    except Exception as e:
        logger.error(f"删除概念失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除概念失败: {e}"
        )

@router.delete("/relation/{relation_id}")
async def delete_relation(
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除概念关系"""
    relation = db.query(ConceptRelation).filter(ConceptRelation.id == relation_id).first()
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关系不存在"
        )
    
    # 删除关系
    db.delete(relation)
    db.commit()
    
    return {"message": "关系已成功删除"}

# 修改返回模型以包含更多相似度细节
class DetailedSimilarity(BaseModel):
    similarity: float
    shared_concepts: int
    concept_similarity: float
    title_similarity: float
    author_similarity: float
    venue_similarity: float
    year_similarity: float

# 添加计算两篇特定论文相似度的接口
@router.post("/two-papers-similarity", response_model=DetailedSimilarity)
async def calculate_two_papers_similarity(
    paper_id1: int = Body(..., embed=True),
    paper_id2: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """计算两篇特定论文之间的综合相似度"""
    # 检查论文是否存在
    paper1 = db.query(Paper).filter(Paper.id == paper_id1, Paper.user_id == current_user.id).first()
    if not paper1:
        raise HTTPException(status_code=404, detail="论文1不存在或无权访问")
    
    paper2 = db.query(Paper).filter(Paper.id == paper_id2, Paper.user_id == current_user.id).first()
    if not paper2:
        raise HTTPException(status_code=404, detail="论文2不存在或无权访问")
    
    # 获取论文1的概念
    paper1_concepts = db.query(Concept.id).join(
        paper_concepts, Concept.id == paper_concepts.c.concept_id
    ).filter(paper_concepts.c.paper_id == paper_id1).all()
    
    paper1_concept_ids = {concept.id for concept in paper1_concepts}
    if not paper1_concept_ids:
        # 如果论文没有关联概念，先尝试提取
        await extract_concepts_from_paper(paper_id1, db, current_user)
        
        # 重新查询概念
        paper1_concepts = db.query(Concept.id).join(
            paper_concepts, Concept.id == paper_concepts.c.concept_id
        ).filter(paper_concepts.c.paper_id == paper_id1).all()
        paper1_concept_ids = {concept.id for concept in paper1_concepts}
        
        if not paper1_concept_ids:
            raise HTTPException(status_code=400, detail="无法从论文1中提取概念")
    
    # 获取论文2的概念
    paper2_concepts = db.query(Concept.id).join(
        paper_concepts, Concept.id == paper_concepts.c.concept_id
    ).filter(paper_concepts.c.paper_id == paper_id2).all()
    
    paper2_concept_ids = {concept.id for concept in paper2_concepts}
    if not paper2_concept_ids:
        # 如果论文没有关联概念，先尝试提取
        await extract_concepts_from_paper(paper_id2, db, current_user)
        
        # 重新查询概念
        paper2_concepts = db.query(Concept.id).join(
            paper_concepts, Concept.id == paper_concepts.c.concept_id
        ).filter(paper_concepts.c.paper_id == paper_id2).all()
        paper2_concept_ids = {concept.id for concept in paper2_concepts}
        
        if not paper2_concept_ids:
            raise HTTPException(status_code=400, detail="无法从论文2中提取概念")
    
    # 计算共享概念数量
    shared_concepts = len(paper1_concept_ids.intersection(paper2_concept_ids))
    
    # 计算各维度相似度
    # 1. 概念相似度 (Jaccard系数)
    concept_union = len(paper1_concept_ids.union(paper2_concept_ids))
    concept_similarity = shared_concepts / concept_union if concept_union > 0 else 0
    
    # 2. 标题相似度
    title_similarity = calculate_text_similarity(paper1.title, paper2.title)
    
    # 3. 作者相似度
    author_similarity = calculate_author_similarity(paper1.authors, paper2.authors)
    
    # 4. 期刊/会议相似度
    # 整合论文的venue和journal字段，确保非空比较
    paper1_venue = paper1.venue if paper1.venue else paper1.journal
    paper2_venue = paper2.venue if paper2.venue else paper2.journal
    venue_similarity = calculate_venue_similarity(paper1_venue, paper2_venue)
    
    # 5. 年份相近度
    year_similarity = calculate_year_similarity(paper1.year, paper2.year)
    
    # 计算综合相似度
    comprehensive_similarity = calculate_comprehensive_similarity(
        paper1, paper2, paper1_concept_ids, paper2_concept_ids, shared_concepts
    )
    
    return {
        "similarity": comprehensive_similarity,
        "shared_concepts": shared_concepts,
        "concept_similarity": concept_similarity,
        "title_similarity": title_similarity,
        "author_similarity": author_similarity, 
        "venue_similarity": venue_similarity,
        "year_similarity": year_similarity
    }

@router.put("/concept/{concept_id}/category", response_model=ConceptSchema)
async def update_concept_category(
    concept_id: int,
    category: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新概念的类别"""
    try:
        concept = db.query(Concept).filter(Concept.id == concept_id).first()
        
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="概念不存在"
            )
        
        # 更新类别
        concept.category = category
        db.commit()
        db.refresh(concept)
        
        return concept
    except Exception as e:
        logger.error(f"更新概念类别失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新概念类别失败: {e}"
        ) 
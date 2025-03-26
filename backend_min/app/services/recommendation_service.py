from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Tuple, Any, Optional
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
import logging
from fastapi import HTTPException
from ..database import get_db, SessionLocal
from ..models import (
    Paper, Tag, User, Concept, ConceptRelation, 
    ReadingHistory, Recommendation, UserInterest,
    Journal, LatestPaper, Note, paper_tag
)
from ..services.journal_service import JournalService
import random
import time

class RecommendationService:
    """文献推荐服务"""

    def __init__(self):
        """初始化推荐服务"""
        self._cache = {}
        self._cache_timeout = timedelta(hours=1)
        self._concept_vectors = {}  # 缓存概念向量
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _get_cached_recommendations(self, user_id: int) -> List[Tuple[Paper, float, str]]:
        """从缓存获取推荐结果"""
        if user_id in self._cache:
            cached_data = self._cache[user_id]
            if datetime.now() - cached_data['timestamp'] < self._cache_timeout:
                return cached_data['recommendations']
        return None

    def _cache_recommendations(self, user_id: int, recommendations: List[Tuple[Paper, float, str]]):
        """缓存推荐结果"""
        self._cache[user_id] = {
            'recommendations': recommendations,
            'timestamp': datetime.now()
        }

    def _invalidate_cache(self, user_id: int):
        """使缓存失效"""
        if user_id in self._cache:
            del self._cache[user_id]

    def _get_concept_vector(self, paper_id: int) -> Dict[int, float]:
        """获取论文的概念向量(带缓存)"""
        if paper_id in self._concept_vectors:
            return self._concept_vectors[paper_id]
        
        paper = self.db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return {}
            
        vector = {concept.id: 1.0 for concept in paper.concepts}
        self._concept_vectors[paper_id] = vector
        return vector

    def record_reading_history(
        self,
        db: Session,
        user_id: int,
        paper_id: int,
        duration: int = None,
        interaction_type: str = "read",
        rating: float = None
    ) -> ReadingHistory:
        """记录用户阅读历史"""
        reading_history = ReadingHistory(
            user_id=user_id,
            paper_id=paper_id,
            read_time=datetime.utcnow(),
            duration=duration,
            interaction_type=interaction_type,
            rating=rating
        )
        
        db.add(reading_history)
        db.commit()
        db.refresh(reading_history)
        
        # 记录阅读历史后使缓存失效
        self._invalidate_cache(user_id)
        return reading_history

    def get_user_interests(self, db: Session, user_id: int) -> Dict[int, float]:
        """获取用户兴趣向量（基于概念）"""
        # 初始化用户兴趣
        interests = {}
        
        # 从阅读历史中提取概念权重
        read_papers = db.query(ReadingHistory.paper_id).filter(
            ReadingHistory.user_id == user_id
        ).distinct().all()
        
        read_paper_ids = [p[0] for p in read_papers]
        
        for paper_id in read_paper_ids:
            # 获取论文相关的概念
            paper_concepts = db.query(Concept, "paper_concepts.weight").join(
                "paper_concepts"
            ).filter(
                "paper_concepts.paper_id" == paper_id
            ).all()
            
            for concept, weight in paper_concepts:
                if concept.id not in interests:
                    interests[concept.id] = weight
                else:
                    interests[concept.id] += weight
        
        # 从笔记中提取概念权重
        notes = db.query(Note).filter(Note.user_id == user_id).all()
        
        for note in notes:
            # 获取笔记相关的概念
            note_concepts = db.query(Concept, "note_concepts.weight").join(
                "note_concepts"
            ).filter(
                "note_concepts.note_id" == note.id
            ).all()
            
            for concept, weight in note_concepts:
                if concept.id not in interests:
                    interests[concept.id] = weight
                else:
                    interests[concept.id] += weight
        
        # 归一化兴趣向量
        if interests:
            max_weight = max(interests.values())
            for concept_id in interests:
                interests[concept_id] /= max_weight
        
        return interests

    def calculate_paper_similarity(
        self,
        db: Session,
        paper_id: int,
        user_interests: Dict[int, float]
    ) -> float:
        """计算论文与用户兴趣的相似度"""
        # 如果用户没有兴趣，返回0
        if not user_interests:
            return 0.0
        
        # 获取论文的概念
        paper_concepts = db.query(Concept, "paper_concepts.weight").join(
            "paper_concepts"
        ).filter(
            "paper_concepts.paper_id" == paper_id
        ).all()
        
        # 如果论文没有概念，返回0
        if not paper_concepts:
            return 0.0
        
        # 计算余弦相似度
        paper_vector = {}
        for concept, weight in paper_concepts:
            paper_vector[concept.id] = weight
        
        dot_product = 0.0
        paper_magnitude = 0.0
        user_magnitude = 0.0
        
        for concept_id, weight in paper_vector.items():
            paper_magnitude += weight * weight
            if concept_id in user_interests:
                dot_product += weight * user_interests[concept_id]
        
        for weight in user_interests.values():
            user_magnitude += weight * weight
        
        paper_magnitude = np.sqrt(paper_magnitude)
        user_magnitude = np.sqrt(user_magnitude)
        
        # 避免除以零
        if paper_magnitude * user_magnitude == 0:
            return 0.0
        
        return dot_product / (paper_magnitude * user_magnitude)

    def generate_recommendations(self, db: Session, user_id: int, limit: int = 10) -> List[Recommendation]:
        """生成推荐，综合用户兴趣、阅读历史和最新论文"""
        try:
            # 开始前先回滚任何未提交的事务，确保当前session是干净的
            db.rollback()

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # 获取用户兴趣
            user_interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
            interest_concepts = [interest.concept_id for interest in user_interests]
            
            # 已推荐过的论文
            existing_recommendations = db.query(Recommendation.paper_id).filter(
                Recommendation.user_id == user_id
            ).all()
            existing_paper_ids = [rec[0] for rec in existing_recommendations]

            # 已阅读过的论文
            read_papers = db.query(ReadingHistory.paper_id).filter(
                ReadingHistory.user_id == user_id
            ).all()
            read_paper_ids = [p[0] for p in read_papers]

            # 排除已推荐和已读过的论文
            excluded_paper_ids = set(existing_paper_ids + read_paper_ids)

            # 基于内容的推荐 (兴趣相关)
            interest_based_recs = self._get_interest_based_recommendations(
                db, user_id, interest_concepts, excluded_paper_ids, limit=limit//2
            )
            
            # 基于协同过滤的推荐 (阅读历史相关)
            cf_recs = self._get_collaborative_filtering_recommendations(
                db, user_id, excluded_paper_ids, limit=limit//4
            )
            
            # 基于最新论文的推荐
            latest_paper_recs = self._get_latest_paper_recommendations(
                db, user_id, interest_concepts, excluded_paper_ids, limit=limit//4
            )
            
            # 合并推荐结果
            all_recommendations = interest_based_recs + cf_recs + latest_paper_recs
            
            # 先删除该用户的所有现有推荐，使用单独的事务
            try:
                db.query(Recommendation).filter(
                    Recommendation.user_id == user_id
                ).delete(synchronize_session=False)
                db.commit()
            except Exception as e:
                db.rollback()
                self.logger.error(f"Error deleting old recommendations: {e}")
                # 继续处理，不影响后续操作
            
            # 开始一个新事务来保存新的推荐
            try:
                # 保存新的推荐
                for rec in all_recommendations:
                    # 检查paper_id是否存在
                    if not db.query(Paper).filter(Paper.id == rec["paper_id"]).first():
                        self.logger.warning(f"跳过不存在的论文ID: {rec['paper_id']}")
                        continue

                    recommendation = Recommendation(
                        user_id=user_id,
                        paper_id=rec["paper_id"],
                        score=rec["score"],
                        reason=rec["reason"]
                    )
                    db.add(recommendation)
                
                db.commit()
            except Exception as e:
                db.rollback()
                self.logger.error(f"Error saving recommendations: {e}")
                # 即使保存推荐失败，也继续处理
            
            # 返回最新的推荐
            return db.query(Recommendation).filter(
                Recommendation.user_id == user_id
            ).order_by(Recommendation.score.desc()).limit(limit).all()
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error in generate_recommendations: {e}")
            # 返回空列表而不是抛出异常，以确保前端仍然能够展示页面
            return []

    def _get_interest_based_recommendations(
        self, db: Session, user_id: int, interest_concepts: List[int], 
        excluded_paper_ids: set, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """基于用户兴趣的推荐"""
        recommendations = []
        
        try:
            # 获取用户兴趣的概念名称，用于匹配论文
            concept_names = []
            if interest_concepts:
                concepts = db.query(Concept).filter(Concept.id.in_(interest_concepts)).all()
                concept_names = [c.name.lower() for c in concepts if c.name]
            
            # 获取所有符合条件的论文
            query = db.query(Paper)
            
            # 排除已经推荐过或已读过的论文
            if excluded_paper_ids:
                query = query.filter(Paper.id.notin_(excluded_paper_ids))
            
            # 获取最近100篇论文进行评分
            papers = query.order_by(Paper.publication_date.desc()).limit(100).all()
            
            for paper in papers:
                paper_id = paper.id
                relevance_score = 0.0
                relevance_reason = []
                
                # 计算与用户兴趣的相关性（基于关键词匹配）
                # 如果论文标题或摘要中包含用户感兴趣的概念，则提高分数
                
                # 来自高质量期刊的加分
                if paper.journal_id:
                    journal = db.query(Journal).filter(Journal.id == paper.journal_id).first()
                    if journal:
                        if journal.ranking == "CCF-A" or journal.ranking == "A" or journal.ranking == "A+":
                            relevance_score += 0.2
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}类期刊）")
                        elif journal.ranking == "CCF-B" or journal.ranking == "B":
                            relevance_score += 0.15
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}类期刊）")
                        elif journal.ranking == "CCF-C" or journal.ranking == "C":
                            relevance_score += 0.1
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}类期刊）")
                        elif journal.ranking == "SCI" or journal.ranking == "SSCI":
                            relevance_score += 0.15
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}）")
                        elif journal.ranking == "CSSCI":
                            relevance_score += 0.12
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}）")
                        elif journal.ranking == "EI":
                            relevance_score += 0.1
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}收录）")
                        else:
                            relevance_score += 0.05
                            relevance_reason.append(f"来自{journal.name}")
                
                # 与用户兴趣的匹配度
                if concept_names:
                    match_count = 0
                    for concept in concept_names:
                        # 检查概念是否在标题或摘要中
                        if (paper.title and concept in paper.title.lower()) or \
                           (paper.abstract and concept in paper.abstract.lower()):
                            match_count += 1
                    
                    if match_count > 0:
                        concept_bonus = min(0.3, match_count * 0.1)  # 最多加0.3分
                        relevance_score += concept_bonus
                        relevance_reason.append(f"与您的{match_count}个研究兴趣相关")
                
                # 时效性加成
                days_old = 0
                if paper.publication_date:
                    days_old = (datetime.now() - paper.publication_date).days
                
                recency_bonus = 0
                if days_old < 30:  # 一个月内
                    recency_bonus = 0.2
                    relevance_reason.append("近期发布的最新研究")
                elif days_old < 90:  # 三个月内
                    recency_bonus = 0.1
                    relevance_reason.append("近三月内发布的研究")
                
                relevance_score += recency_bonus
                
                # 限制分数范围在0-1之间
                final_score = min(1.0, max(0.0, relevance_score))
                
                recommendations.append({
                    "paper_id": paper_id,
                    "score": final_score,
                    "reason": "、".join(relevance_reason)
                })
                
                # 如果已经收集了足够的推荐，就停止
                if len(recommendations) >= limit:
                    break
            
            # 按分数排序
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error in interest-based recommendations: {e}")
            # 确保异常不会影响数据库状态
            db.rollback()
            # 出错时返回空列表，不影响其他推荐逻辑
        
        return recommendations[:limit]

    def _get_collaborative_filtering_recommendations(
        self, db: Session, user_id: int, excluded_paper_ids: set, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """基于协同过滤的推荐"""
        recommendations = []
        
        try:
            # 获取用户阅读历史
            user_history = db.query(ReadingHistory).filter(
                ReadingHistory.user_id == user_id
            ).all()
            
            if not user_history:
                return []
                
            # 获取与当前用户有共同阅读记录的用户
            # 这里使用简化的协同过滤方法，找出阅读过相同论文的用户
            paper_ids = [h.paper_id for h in user_history]
            similar_users = db.query(ReadingHistory.user_id).filter(
                ReadingHistory.paper_id.in_(paper_ids),
                ReadingHistory.user_id != user_id
            ).distinct().all()
            
            similar_user_ids = [u[0] for u in similar_users]
            
            if not similar_user_ids:
                # 如果没有相似用户，返回空列表
                return []
            
            # 获取相似用户阅读过但当前用户未阅读的论文
            candidate_papers = db.query(Paper).join(
                ReadingHistory, ReadingHistory.paper_id == Paper.id
            ).filter(
                ReadingHistory.user_id.in_(similar_user_ids),
                Paper.id.notin_([h.paper_id for h in user_history]),
                Paper.id.notin_(excluded_paper_ids) if excluded_paper_ids else True
            ).distinct().all()
            
            # 计算推荐分数
            for paper in candidate_papers:
                # 计算有多少相似用户阅读过这篇论文
                read_count = db.query(func.count(ReadingHistory.id)).filter(
                    ReadingHistory.paper_id == paper.id,
                    ReadingHistory.user_id.in_(similar_user_ids)
                ).scalar()
                
                # 相似用户阅读量作为基础分数
                score = min(1.0, read_count / len(similar_user_ids))
                
                # 论文评分因素
                if paper.average_rating:
                    score = score * (0.5 + 0.5 * min(1.0, paper.average_rating / 5.0))
                
                # 构造推荐原因
                reason = "与您阅读习惯相似的用户也阅读了此论文"
                
                # 获取论文的期刊信息
                if paper.journal_id:
                    journal = db.query(Journal).filter(Journal.id == paper.journal_id).first()
                    if journal:
                        category = journal.category or "学术"
                        ranking = journal.ranking or ""
                        
                        # 根据期刊类别和排名构建推荐原因
                        if ranking:
                            if ranking == "CCF-A":
                                reason = f"来自CCF-A类期刊的{category}论文"
                            elif ranking == "CSSCI":
                                reason = f"来自CSSCI核心期刊的{category}论文"
                            else:
                                reason = f"来自{journal.name}（{ranking}）的{category}论文"
                        else:
                            reason = f"来自{journal.name}的{category}论文"
                elif paper.source:
                    reason = f"来自{paper.source}的开源文献"
                
                recommendations.append({
                    "paper_id": paper.id,
                    "score": score,
                    "reason": reason
                })
            
            # 按分数排序
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error in collaborative filtering recommendations: {e}")
            # 确保异常不会影响数据库状态
            db.rollback()
            # 出错时返回空列表，不影响其他推荐逻辑
        
        return recommendations[:limit]

    def _get_latest_paper_recommendations(
        self, db: Session, user_id: int, interest_concepts: List[int], 
        excluded_paper_ids: set, limit: int = 2
    ) -> List[Dict[str, Any]]:
        """基于最新论文的推荐"""
        recommendations = []
        
        try:
            # 获取用户兴趣的概念名称，用于匹配论文
            concept_names = []
            if interest_concepts:
                concepts = db.query(Concept).filter(Concept.id.in_(interest_concepts)).all()
                concept_names = [c.name.lower() for c in concepts if c.name]
            
            # 获取两周内的最新论文
            two_weeks_ago = datetime.now() - timedelta(days=14)
            query = db.query(LatestPaper).filter(LatestPaper.created_at >= two_weeks_ago)
            
            # 获取最新论文
            latest_papers = query.order_by(LatestPaper.created_at.desc()).limit(50).all()
            
            for latest_paper in latest_papers:
                # 跳过已经推荐过或阅读过的论文
                if latest_paper.paper_id and latest_paper.paper_id in excluded_paper_ids:
                    continue
                
                paper_id = latest_paper.paper_id
                if not paper_id:
                    continue
                
                relevance_score = 0.2  # 基础分数，因为是最新的
                relevance_reason = ["最新发布的论文"]
                
                # 来自高质量期刊的加分
                if latest_paper.journal_id:
                    journal = db.query(Journal).filter(Journal.id == latest_paper.journal_id).first()
                    if journal:
                        if journal.ranking == "CCF-A" or journal.ranking == "A" or journal.ranking == "A+":
                            relevance_score += 0.3
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}类期刊）")
                        elif journal.ranking == "CCF-B" or journal.ranking == "B":
                            relevance_score += 0.2
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}类期刊）")
                        elif journal.ranking == "CCF-C" or journal.ranking == "C":
                            relevance_score += 0.1
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}类期刊）")
                        elif journal.ranking in ["SCI", "SSCI", "CSSCI", "EI"]:
                            relevance_score += 0.2
                            relevance_reason.append(f"来自{journal.name}（{journal.ranking}收录）")
                        else:
                            relevance_score += 0.05
                            relevance_reason.append(f"来自{journal.name}")
                
                # 与用户兴趣的匹配度
                paper = db.query(Paper).filter(Paper.id == paper_id).first()
                if paper and concept_names:
                    match_count = 0
                    for concept in concept_names:
                        # 检查概念是否在标题或摘要中
                        if (paper.title and concept in paper.title.lower()) or \
                           (paper.abstract and concept in paper.abstract.lower()):
                            match_count += 1
                    
                    if match_count > 0:
                        concept_bonus = min(0.3, match_count * 0.1)  # 最多加0.3分
                        relevance_score += concept_bonus
                        relevance_reason.append(f"与您的{match_count}个研究兴趣相关")
                
                # 时效性加成
                days_old = 0
                if latest_paper.publication_date:
                    days_old = (datetime.now() - latest_paper.publication_date).days
                
                recency_bonus = 0
                if days_old < 7:  # 一周内
                    recency_bonus = 0.3
                    relevance_reason.append("一周内发布的研究")
                elif days_old < 14:  # 两周内
                    recency_bonus = 0.2
                    relevance_reason.append("两周内发布的研究")
                
                relevance_score += recency_bonus
                
                # 限制分数范围在0-1之间
                final_score = min(1.0, max(0.0, relevance_score))
                
                recommendations.append({
                    "paper_id": paper_id,
                    "score": final_score,
                    "reason": "、".join(relevance_reason)
                })
                
                # 如果已经收集了足够的推荐，就停止
                if len(recommendations) >= limit:
                    break
            
            # 按分数排序
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error in latest paper recommendations: {e}")
            # 确保异常不会影响数据库状态
            db.rollback()
            # 出错时返回空列表，不影响其他推荐逻辑
        
        return recommendations[:limit]

    def _generate_recommendation_reason(
        self,
        db: Session,
        paper: Paper,
        score: float,
        user_interests: Dict[int, float]
    ) -> str:
        """生成推荐原因"""
        reasons = []
        
        # 基于相似度
        if score > 0.8:
            reasons.append("与您的兴趣高度相关")
        elif score > 0.5:
            reasons.append("与您的兴趣相关")
        elif score > 0.3:
            reasons.append("与您的部分兴趣相关")
        
        # 基于引用数
        if paper.citations and paper.citations > 100:
            reasons.append(f"被广泛引用（{paper.citations}次）")
        elif paper.citations and paper.citations > 50:
            reasons.append(f"引用数较多（{paper.citations}次）")
        
        # 基于出版年份
        current_year = datetime.utcnow().year
        if paper.year and paper.year >= current_year - 2:
            reasons.append("最新研究")
        elif paper.year and paper.year >= current_year - 5:
            reasons.append("近期研究")
        
        # 基于共同概念
        if user_interests:
            paper_concepts = db.query(Concept, "paper_concepts.weight").join(
                "paper_concepts"
            ).filter(
                "paper_concepts.paper_id" == paper.id
            ).all()
            
            common_concepts = []
            for concept, _ in paper_concepts:
                if concept.id in user_interests and user_interests[concept.id] > 0.5:
                    common_concepts.append(concept.name)
            
            if common_concepts:
                if len(common_concepts) > 3:
                    concepts_text = "多个您感兴趣的主题"
                else:
                    concepts_text = "、".join(common_concepts[:3])
                reasons.append(f"包含{concepts_text}")
        
        if not reasons:
            return "基于您的阅读历史推荐"
        
        return "；".join(reasons)

    def get_user_recommendations(self, db: Session, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的推荐论文"""
        return self.get_recommendations(db, user_id, limit)

    def refresh_recommendations(self, db: Session, user_id: int) -> None:
        """刷新用户推荐"""
        self.logger.info(f"刷新用户 {user_id} 的推荐")
        self._invalidate_cache(user_id)
        self.generate_recommendations(db, user_id)
        self.logger.info(f"用户 {user_id} 的推荐已刷新")

    def get_recommendations(self, db: Session, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的推荐，如果没有则生成"""
        recommendations = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).order_by(Recommendation.score.desc()).limit(limit).all()
        
        # 如果没有推荐，则生成新的推荐
        if not recommendations:
            recommendations = self.generate_recommendations(db, user_id, limit)
        
        # 返回推荐结果，包含论文信息
        result = []
        for rec in recommendations:
            paper = db.query(Paper).filter(Paper.id == rec.paper_id).first()
            if paper:
                paper_data = {
                    "id": rec.id,
                    "paper_id": rec.paper_id,
                    "score": rec.score,
                    "reason": rec.reason,
                    "paper": {
                        "id": paper.id,
                        "title": paper.title,
                        "authors": paper.authors,
                        "abstract": paper.abstract,
                        "doi": paper.doi,
                        "publication_date": paper.publication_date
                    }
                }
                
                # 如果Paper对象有url属性则添加
                if hasattr(paper, 'url'):
                    paper_data["paper"]["url"] = paper.url
                elif hasattr(paper, 'doi') and paper.doi:
                    # 如果有DOI，可以构建一个通用的DOI链接
                    paper_data["paper"]["url"] = f"https://doi.org/{paper.doi}"
                else:
                    paper_data["paper"]["url"] = ""
                
                # 如果Paper对象有source属性则添加
                if hasattr(paper, 'source'):
                    paper_data["paper"]["source"] = paper.source
                else:
                    paper_data["paper"]["source"] = ""
                
                result.append(paper_data)
        
        return result

    def get_random_recommendations(self, db: Session, user_id: int, category: Optional[str] = None, limit: int = 10, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """获取随机推荐（可按分类筛选）
        
        参数:
            db: 数据库会话
            user_id: 用户ID
            category: 可选的分类筛选
            limit: 返回结果数量限制
            force_refresh: 是否强制刷新（不使用缓存）
        """
        try:
            self.logger.info(f"为用户 {user_id} 获取随机推荐，领域: {category}")
            
            # 构建查询，获取所有有效的论文
            query = db.query(Paper).filter(
                Paper.is_public == True,  # 只获取公开的论文
                Paper.title.isnot(None),  # 确保标题不为空
                Paper.title != "",        # 确保标题不为空字符串
                # 确保DOI不为空字符串(允许为NULL)
                or_(Paper.doi.isnot(None), Paper.doi != "")
            )
            
            # 如果指定了分类，进行过滤
            if category:
                # 基于期刊分类过滤
                journal_ids = db.query(Journal.id).filter(Journal.category == category).all()
                journal_ids = [j[0] for j in journal_ids]
                
                if journal_ids:
                    query = query.filter(Paper.journal_id.in_(journal_ids))
                else:
                    # 如果找不到匹配的期刊，尝试在标题和摘要中搜索
                    query = query.filter(
                        or_(
                            func.lower(Paper.title).like(f"%{category.lower()}%"),
                            func.lower(Paper.abstract).like(f"%{category.lower()}%")
                        )
                    )
            
            # 随机选择论文
            # 在SQLite中实现随机排序
            total_papers = query.count()
            if total_papers == 0:
                return []
                
            # 如果论文数量少于请求数量，返回所有论文
            if total_papers <= limit:
                papers = query.all()
            else:
                # 随机选择offset
                offset = random.randint(0, max(0, total_papers - limit))
                papers = query.order_by(func.random()).offset(offset).limit(limit).all()
            
            # 构建推荐结果
            results = []
            for paper in papers:
                # 构建推荐原因
                reason = self._generate_random_recommendation_reason(db, paper, category)
                
                # 添加到结果
                results.append({
                    "id": len(results) + 1,  # 生成递增的ID
                    "paper_id": paper.id,
                    "score": random.uniform(0.5, 0.9),  # 随机分数
                    "reason": reason,
                    "paper": {
                        "id": paper.id,
                        "title": paper.title,
                        "authors": paper.authors,
                        "abstract": paper.abstract,
                        "doi": paper.doi or "",
                        "url": paper.url or "",
                        "publication_date": paper.publication_date.isoformat() if paper.publication_date else "",
                        "source": paper.source or ""
                    }
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"获取随机推荐失败: {e}")
            db.rollback()  # 确保任何未完成的事务被回滚
            # 返回空列表而不是抛出异常
            return []
            
    def _generate_random_recommendation_reason(self, db: Session, paper: Paper, category: Optional[str] = None) -> str:
        """为随机推荐生成推荐原因"""
        try:
            reasons = []
            
            # 如果论文有期刊信息
            if paper.journal_id:
                journal = db.query(Journal).filter(Journal.id == paper.journal_id).first()
                if journal:
                    journal_category = journal.category or "学术"
                    journal_name = journal.name or ""
                    journal_ranking = journal.ranking or ""
                    
                    # 根据不同的排名体系构建推荐原因
                    if journal_ranking.startswith("CCF-"):  # CCF分类
                        reasons.append(f"来自{journal_ranking}类期刊的{journal_category}论文")
                    elif journal_ranking == "CSSCI":  # CSSCI核心
                        reasons.append(f"来自CSSCI核心期刊的{journal_category}论文")
                    elif journal_ranking in ["SCI", "SSCI", "EI"]:  # 国际索引
                        reasons.append(f"来自{journal_name}（{journal_ranking}收录）的{journal_category}论文")
                    elif journal_ranking == "预印本":  # 预印本平台
                        reasons.append(f"来自{journal_name}预印本平台的{journal_category}论文")
                    elif journal_ranking == "数据库":  # 数据库平台
                        reasons.append(f"来自{journal_name}数据库的{journal_category}研究资料")
                    else:
                        reasons.append(f"来自{journal_name}的{journal_category}论文")
            
            # 基于分类
            if category and category != "全部":
                reasons.append(f"随机推荐的{category}领域论文")
            else:
                reasons.append("随机推荐的开放获取论文")
            
            # 如果没有构建出任何原因，给一个默认值
            if not reasons:
                return "随机推荐的学术论文"
            
            return "；".join(reasons)
        except Exception as e:
            self.logger.error(f"生成随机推荐原因失败: {e}")
            return "随机推荐的学术论文" 
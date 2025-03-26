from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..models import Paper, Concept, paper_concepts
from ..schemas.paper import PaperWithTags

logger = logging.getLogger(__name__)

class GraphService:
    def get_paper_concepts(self, db: Session, paper_id: int) -> List[Dict[str, Any]]:
        """获取论文相关的概念"""
        try:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not paper:
                return []
            
            concepts = paper.concepts
            return [
                {
                    "id": concept.id,
                    "name": concept.name,
                    "description": concept.description,
                    "weight": concept.weight
                }
                for concept in concepts
            ]
        except Exception as e:
            logger.error(f"获取论文概念失败: {e}")
            raise
    
    def get_concept_papers(self, db: Session, concept_id: int) -> List[Dict[str, Any]]:
        """获取概念相关的论文"""
        try:
            concept = db.query(Concept).filter(Concept.id == concept_id).first()
            if not concept:
                return []
            
            papers = concept.papers
            return [
                {
                    "id": paper.id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.year,
                    "doi": paper.doi
                }
                for paper in papers
            ]
        except Exception as e:
            logger.error(f"获取概念论文失败: {e}")
            raise
    
    def add_concept_to_paper(self, db: Session, paper_id: int, concept_id: int) -> bool:
        """将概念添加到论文"""
        try:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            concept = db.query(Concept).filter(Concept.id == concept_id).first()
            
            if not paper or not concept:
                return False
            
            if concept not in paper.concepts:
                paper.concepts.append(concept)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"添加概念到论文失败: {e}")
            raise
    
    def remove_concept_from_paper(self, db: Session, paper_id: int, concept_id: int) -> bool:
        """从论文中移除概念"""
        try:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            concept = db.query(Concept).filter(Concept.id == concept_id).first()
            
            if not paper or not concept:
                return False
            
            if concept in paper.concepts:
                paper.concepts.remove(concept)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"从论文移除概念失败: {e}")
            raise
    
    def get_paper_graph(self, db: Session, paper_id: int) -> Dict[str, Any]:
        """获取论文的知识图谱"""
        try:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not paper:
                return {}
            
            # 获取论文的概念
            concepts = self.get_paper_concepts(db, paper_id)
            
            # 获取论文的引用关系
            citations = [
                {
                    "id": citation.cited_paper.id,
                    "title": citation.cited_paper.title,
                    "authors": citation.cited_paper.authors,
                    "year": citation.cited_paper.year
                }
                for citation in paper.citations
            ]
            
            cited_by = [
                {
                    "id": citation.paper.id,
                    "title": citation.paper.title,
                    "authors": citation.paper.authors,
                    "year": citation.paper.year
                }
                for citation in paper.cited_by
            ]
            
            return {
                "paper": {
                    "id": paper.id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.year,
                    "doi": paper.doi
                },
                "concepts": concepts,
                "citations": citations,
                "cited_by": cited_by
            }
        except Exception as e:
            logger.error(f"获取论文图谱失败: {e}")
            raise 
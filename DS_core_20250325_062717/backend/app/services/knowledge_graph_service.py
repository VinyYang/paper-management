from typing import List, Dict, Any
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ..models import Paper, Note
from ..database import SessionLocal

class KnowledgeGraphService:
    def __init__(self):
        self.graph = nx.Graph()
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def build_graph(self) -> Dict[str, Any]:
        """构建知识图谱"""
        db = SessionLocal()
        try:
            # 获取所有文献和笔记
            papers = db.query(Paper).all()
            notes = db.query(Note).all()
            
            # 清空现有图
            self.graph.clear()
            
            # 添加文献节点
            for paper in papers:
                self.graph.add_node(
                    f"paper_{paper.id}",
                    name=paper.title,
                    category=0,  # 文献类别
                    type="paper"
                )
            
            # 添加笔记节点
            for note in notes:
                self.graph.add_node(
                    f"note_{note.id}",
                    name=f"Note on {note.paper.title}",
                    category=1,  # 笔记类别
                    type="note"
                )
                # 连接笔记和文献
                self.graph.add_edge(
                    f"note_{note.id}",
                    f"paper_{note.paper_id}",
                    type="belongs_to"
                )
            
            # 计算文献相似度
            paper_texts = [f"{p.title} {p.abstract}" for p in papers]
            tfidf_matrix = self.vectorizer.fit_transform(paper_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # 添加文献间的相似度边
            for i in range(len(papers)):
                for j in range(i + 1, len(papers)):
                    if similarity_matrix[i, j] > 0.3:  # 相似度阈值
                        self.graph.add_edge(
                            f"paper_{papers[i].id}",
                            f"paper_{papers[j].id}",
                            type="similar",
                            weight=float(similarity_matrix[i, j])
                        )
            
            # 提取关键词作为概念节点
            feature_names = self.vectorizer.get_feature_names_out()
            for i, paper in enumerate(papers):
                # 获取文献的top关键词
                paper_vector = tfidf_matrix[i].toarray().flatten()
                top_indices = np.argsort(paper_vector)[-5:]  # 取top5关键词
                
                for idx in top_indices:
                    if paper_vector[idx] > 0.1:  # 关键词权重阈值
                        concept = feature_names[idx]
                        concept_id = f"concept_{concept}"
                        
                        # 添加概念节点
                        if not self.graph.has_node(concept_id):
                            self.graph.add_node(
                                concept_id,
                                name=concept,
                                category=2,  # 概念类别
                                type="concept"
                            )
                        
                        # 连接文献和概念
                        self.graph.add_edge(
                            f"paper_{paper.id}",
                            concept_id,
                            type="contains",
                            weight=float(paper_vector[idx])
                        )
            
            # 转换为前端需要的格式
            nodes = []
            links = []
            
            for node in self.graph.nodes(data=True):
                nodes.append({
                    "id": node[0],
                    "name": node[1]["name"],
                    "category": node[1]["category"],
                    "symbolSize": 10 + len(list(self.graph.neighbors(node[0]))) * 2
                })
            
            for edge in self.graph.edges(data=True):
                links.append({
                    "source": edge[0],
                    "target": edge[1],
                    "value": edge[2].get("weight", 1)
                })
            
            return {
                "nodes": nodes,
                "links": links
            }
            
        finally:
            db.close()
    
    def update_graph(self, paper_id: int) -> Dict[str, Any]:
        """更新知识图谱(添加新文献后)"""
        db = SessionLocal()
        try:
            # 获取新添加的文献
            new_paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not new_paper:
                raise ValueError(f"Paper with id {paper_id} not found")
            
            # 添加新文献节点
            self.graph.add_node(
                f"paper_{new_paper.id}",
                name=new_paper.title,
                category=0,
                type="paper"
            )
            
            # 计算与新文献的相似度
            paper_texts = [f"{p.title} {p.abstract}" for p in db.query(Paper).all()]
            tfidf_matrix = self.vectorizer.fit_transform(paper_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # 添加相似度边
            new_paper_idx = paper_texts.index(f"{new_paper.title} {new_paper.abstract}")
            for i in range(len(paper_texts)):
                if i != new_paper_idx and similarity_matrix[new_paper_idx, i] > 0.3:
                    self.graph.add_edge(
                        f"paper_{new_paper.id}",
                        f"paper_{i}",
                        type="similar",
                        weight=float(similarity_matrix[new_paper_idx, i])
                    )
            
            # 提取新文献的关键词
            feature_names = self.vectorizer.get_feature_names_out()
            paper_vector = tfidf_matrix[new_paper_idx].toarray().flatten()
            top_indices = np.argsort(paper_vector)[-5:]
            
            for idx in top_indices:
                if paper_vector[idx] > 0.1:
                    concept = feature_names[idx]
                    concept_id = f"concept_{concept}"
                    
                    if not self.graph.has_node(concept_id):
                        self.graph.add_node(
                            concept_id,
                            name=concept,
                            category=2,
                            type="concept"
                        )
                    
                    self.graph.add_edge(
                        f"paper_{new_paper.id}",
                        concept_id,
                        type="contains",
                        weight=float(paper_vector[idx])
                    )
            
            # 转换为前端需要的格式
            nodes = []
            links = []
            
            for node in self.graph.nodes(data=True):
                nodes.append({
                    "id": node[0],
                    "name": node[1]["name"],
                    "category": node[1]["category"],
                    "symbolSize": 10 + len(list(self.graph.neighbors(node[0]))) * 2
                })
            
            for edge in self.graph.edges(data=True):
                links.append({
                    "source": edge[0],
                    "target": edge[1],
                    "value": edge[2].get("weight", 1)
                })
            
            return {
                "nodes": nodes,
                "links": links
            }
            
        finally:
            db.close() 
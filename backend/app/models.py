from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from .database import Base

# 先定义所有关联表
# 论文-标签关联表
paper_tag = Table(
    'paper_tag',
    Base.metadata,
    Column('paper_id', Integer, ForeignKey('papers.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)
                                                          
# 项目-论文关联表
project_paper = Table(
    'project_paper',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('paper_id', Integer, ForeignKey('papers.id'))
)

# 论文-概念关联表
paper_concepts = Table(
    'paper_concepts',
    Base.metadata,
    Column('paper_id', Integer, ForeignKey('papers.id')),
    Column('concept_id', Integer, ForeignKey('concepts.id'))
)

# 定义用户角色枚举
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    PREMIUM = "premium"

# 先定义Paper类，然后引用它
class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    authors = Column(String(1000))
    abstract = Column(Text)
    doi = Column(String(100), unique=True)
    url = Column(String(500))
    pdf_url = Column(String(500))
    publication_date = Column(DateTime)
    year = Column(Integer)  # 添加年份字段
    venue = Column(String(255))  # 发表场所(会议/期刊)
    journal_id = Column(Integer, ForeignKey("journals.id"))
    citation_count = Column(Integer, default=0)
    reference_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    local_pdf_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    journal = Column(String(255))
    source = Column(String(255))
    
    # 关系 (在后面定义)
    user = relationship("User", back_populates="papers")
    notes = None  # 将在后面更新
    tags = None  # 将在后面更新
    citations = None  # 将在后面更新
    cited_by = None  # 将在后面更新
    projects = None  # 将在后面更新
    reading_history = None  # 将在后面更新
    recommendations = None  # 将在后面更新
    concepts = None  # 将在后面更新
    
    def __repr__(self):
        return f"<Paper {self.title}>"

# 更新Paper的关系
Paper.user = relationship("User", back_populates="papers")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    
    # 关系将在后面更新
    papers = None  # 将在后面更新

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    first_name = Column(String(50))
    last_name = Column(String(50))
    avatar_url = Column(String(255))
    fullname = Column(String(100))
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    storage_capacity = Column(Integer, default=1024)  # 存储容量，单位MB，默认1GB
    storage_used = Column(Integer, default=0)  # 已使用存储空间，单位MB
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    notes = relationship("Note", back_populates="user")
    papers = relationship("Paper", back_populates="user")
    projects = relationship("Project", back_populates="user")
    search_histories = relationship("SearchHistory", back_populates="user")
    reading_histories = relationship("ReadingHistory", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    interests = relationship("UserInterest", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

# 现在更新Paper的关系
Paper.tags = relationship("Tag", secondary=paper_tag, back_populates="papers")
Paper.notes = relationship("Note", back_populates="paper")
Paper.projects = relationship("Project", secondary=project_paper, back_populates="papers")
Paper.reading_history = relationship("ReadingHistory", back_populates="paper")
Paper.recommendations = relationship("Recommendation", back_populates="paper")
Paper.concepts = relationship("Concept", secondary=paper_concepts, back_populates="papers")
# 更新journal关系，journal_id指向Journal表
Paper.journal_relation = relationship("Journal", foreign_keys=[Paper.journal_id], back_populates="papers")

# Citation类定义
class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    cited_paper_id = Column(Integer, ForeignKey("papers.id"))
    citation_text = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    paper = relationship("Paper", foreign_keys=[paper_id], back_populates="citations")
    cited_paper = relationship("Paper", foreign_keys=[cited_paper_id], back_populates="cited_by")
    
    def __repr__(self):
        return f"<Citation paper_id={self.paper_id}, cited_paper_id={self.cited_paper_id}>"

# 初始化"被引用"关系
Paper.citations = relationship("Citation", foreign_keys=[Citation.paper_id], back_populates="paper")
Paper.cited_by = relationship("Citation", foreign_keys=[Citation.cited_paper_id], back_populates="cited_paper")

# 更新Tag的关系
Tag.papers = relationship("Paper", secondary=paper_tag, back_populates="tags")

class Journal(Base):
    __tablename__ = "journals"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    issn = Column(String(20))
    impact_factor = Column(Float)
    h_index = Column(Integer)
    description = Column(Text)
    website = Column(String(255))
    abbreviation = Column(String(50))  # 期刊缩写
    ranking = Column(String(50))  # 排名信息
    category = Column(String(100))  # 期刊分类
    url = Column(String(500))  # 期刊网址
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    papers = relationship("Paper", back_populates="journal_relation")
    latest_papers = relationship("LatestPaper", back_populates="journal")
    
    def __repr__(self):
        return f"<Journal {self.name}>"

class LatestPaper(Base):
    __tablename__ = "latest_papers"
    
    id = Column(Integer, primary_key=True)
    journal_id = Column(Integer, ForeignKey("journals.id"))
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)  # 可能关联到Papers表
    title = Column(String(500))  # 添加标题字段
    authors = Column(String(1000))  # 添加作者字段
    abstract = Column(Text)  # 添加摘要字段
    url = Column(String(500))  # 添加URL字段
    publish_date = Column(DateTime)
    publication_date = Column(DateTime)  # 出版日期
    created_at = Column(DateTime, default=datetime.utcnow)
    doi = Column(String(100))  # DOI字段
    
    # 关系
    journal = relationship("Journal", back_populates="latest_papers")
    paper = relationship("Paper", foreign_keys=[paper_id], backref="latest_paper", uselist=False)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 关系
    user = relationship("User", back_populates="projects")
    papers = relationship("Paper", secondary=project_paper, back_populates="projects")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False, default="笔记")
    content = Column(Text, nullable=False)
    page_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    paper = relationship("Paper", back_populates="notes")
    user = relationship("User", back_populates="notes")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String(500), nullable=False)
    result_info = Column(Text)
    doi = Column(String(100))
    url = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="search_histories")

class ReadingHistory(Base):
    __tablename__ = "reading_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    paper_id = Column(Integer, ForeignKey("papers.id"))
    read_time = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, default=0)  # 阅读时长（秒）
    interaction_type = Column(String(50))  # 互动类型：打开、下载、引用等
    rating = Column(Float, default=0)  # 评分
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="reading_histories")
    paper = relationship("Paper", back_populates="reading_history")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    paper_id = Column(Integer, ForeignKey("papers.id"))
    score = Column(Float)
    reason = Column(String(500))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="recommendations")
    paper = relationship("Paper", back_populates="recommendations")

class Concept(Base):
    __tablename__ = "concepts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(Integer, default=0)  # 概念类别：0=基础概念，1=扩展概念，2=主题概念
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    relations_source = relationship("ConceptRelation", foreign_keys="ConceptRelation.source_id", back_populates="source")
    relations_target = relationship("ConceptRelation", foreign_keys="ConceptRelation.target_id", back_populates="target")
    papers = relationship("Paper", secondary="paper_concepts", back_populates="concepts")

class ConceptRelation(Base):
    __tablename__ = "concept_relations"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("concepts.id"))
    target_id = Column(Integer, ForeignKey("concepts.id"))
    relation_type = Column(String(50))  # 关系类型：包含、相关、对立等
    weight = Column(Float, default=1.0)  # 关系权重
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    source = relationship("Concept", foreign_keys=[source_id], back_populates="relations_source")
    target = relationship("Concept", foreign_keys=[target_id], back_populates="relations_target")

# 更新Paper的关系
Paper.tags = relationship("Tag", secondary=paper_tag, back_populates="papers")
Paper.notes = relationship("Note", back_populates="paper")
Paper.projects = relationship("Project", secondary=project_paper, back_populates="papers")
Paper.reading_history = relationship("ReadingHistory", back_populates="paper")
Paper.recommendations = relationship("Recommendation", back_populates="paper")
Paper.concepts = relationship("Concept", secondary=paper_concepts, back_populates="papers")
# 更新journal关系，journal_id指向Journal表
Paper.journal_relation = relationship("Journal", foreign_keys=[Paper.journal_id], back_populates="papers")

class UserInterest(Base):
    __tablename__ = "user_interests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    concept_id = Column(Integer, ForeignKey("concepts.id"))
    weight = Column(Float, default=1.0)  # 兴趣权重
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="interests")
    concept = relationship("Concept")

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(50))  # 活动类型：搜索、浏览、下载等
    content = Column(Text)  # 活动内容
    activity_metadata = Column(Text, nullable=True)  # 额外的元数据，如DOI、URL等
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="activities") 
# 导入实际模型
from .user import User
from .paper import Paper, Tag, paper_tag, paper_concepts
from .note import Note, note_concepts
from .concept import Concept, ConceptRelation
from .project import Project, project_paper
from .journal import Journal, LatestPaper
from .user_interest import UserInterest
from .user_activity import UserActivity
from .search_history import SearchHistory
from .recommendation import Recommendation, ReadingHistory
from .citation import Citation 
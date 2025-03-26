# 完全消除循环导入
# 首先导入数据库基类
from ..database import Base
import enum

# 临时解决方案：重新在本模块中定义所有必需的模型
# 注意：这是一个临时修复，长期应该完成完整的模型重构

# 定义用户角色枚举
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

# 导入实际模型
from .user import User
# 修改导入顺序，先导入project，再导入paper
from .project import Project, project_paper
from .paper import Paper, Tag, paper_tag, paper_concepts
from .note import Note, note_concepts
from .concept import Concept, ConceptRelation
from .journal import Journal, LatestPaper
from .user_interest import UserInterest
from .user_activity import UserActivity
from .search_history import SearchHistory
from .recommendation import Recommendation, ReadingHistory
from .citation import Citation

# 导出所有模型
__all__ = [
    'Base', 'User', 'UserRole', 'Paper', 'Tag', 'Note', 'Concept', 'ConceptRelation',
    'ReadingHistory', 'Recommendation', 'Project', 'SearchHistory',
    'Journal', 'LatestPaper', 'UserInterest', 'UserActivity',
    'Citation', 'paper_tag', 'project_paper', 'paper_concepts', 'note_concepts'
] 
# 路由模块 
from ..routers import papers
from ..routers import projects
from ..routers import users
from ..routers import notes
from ..routers import knowledge_graph as graph
from ..routers import recommendations
from ..routers import tags
from ..routers import activities
from ..routers import search 

__all__ = [
    "papers",
    "notes",
    "tags",
    "activities",
    "search",
    "users",
    "recommendations",
    "graph",
    "projects"
] 
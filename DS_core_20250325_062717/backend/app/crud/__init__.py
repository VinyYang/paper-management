# CRUD操作模块
from .user import (
    get_user, 
    get_user_by_email, 
    get_user_by_username, 
    get_users, 
    create_user, 
    update_user, 
    delete_user, 
    authenticate_user
)
from .paper import (
    get_paper,
    get_papers,
    create_paper,
    update_paper,
    delete_paper,
    get_papers_by_user,
    get_papers_by_concept,
    get_papers_by_citation
)
from .concept import (
    get_concept,
    get_concepts,
    create_concept,
    update_concept,
    delete_concept,
    get_concepts_by_paper,
    get_concepts_by_user
)
from .project import (
    get_project,
    get_projects,
    create_project,
    update_project,
    delete_project,
    get_projects_by_user,
    add_paper_to_project,
    remove_paper_from_project
)
from .note import (
    get_note,
    get_notes,
    create_note,
    update_note,
    delete_note,
    get_notes_by_paper,
    get_notes_by_user
)
from .citation import (
    get_citation,
    get_citations,
    create_citation,
    update_citation,
    delete_citation,
    get_citations_by_paper
)
from .search_history import (
    get_search_history,
    get_search_histories,
    create_search_history,
    update_search_history,
    delete_search_history,
    get_search_histories_by_user,
    clear_user_search_history
)
from .user_activity import (
    get_user_activity,
    create_user_activity,
    get_user_activities_by_user
)
from .user_interest import (
    get_user_interest,
    get_user_interests,
    create_user_interest,
    update_user_interest,
    delete_user_interest,
    get_user_interests_by_user,
    update_interest_weight,
    clear_user_interests
) 
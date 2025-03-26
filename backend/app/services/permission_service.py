from fastapi import HTTPException, status
from ..models import User, UserRole

def check_admin_permission(user: User):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

def check_user_active(user: User):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

def check_owner_permission(user: User, resource_user_id: int):
    if user.role != UserRole.ADMIN and user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此资源"
        ) 
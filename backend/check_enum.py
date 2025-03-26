from app.models import UserRole

def check_enum():
    print("UserRole枚举值:")
    for role in UserRole:
        print(f"- {role.name}: {role.value}")
    
    print("\n检查是否存在PREMIUM角色:")
    print(f"hasattr(UserRole, 'PREMIUM'): {hasattr(UserRole, 'PREMIUM')}")
    
    if hasattr(UserRole, 'PREMIUM'):
        print(f"UserRole.PREMIUM = {UserRole.PREMIUM}")
    else:
        print("UserRole.PREMIUM 不存在")

if __name__ == "__main__":
    check_enum() 
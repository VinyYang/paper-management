from app.database import engine
import sqlalchemy as sa

def check_db():
    with engine.connect() as conn:
        result = conn.execute(sa.text('SELECT username, role FROM users'))
        print("用户角色:")
        for row in result:
            print(f"用户: {row.username}, 角色: {row.role}")

if __name__ == "__main__":
    check_db() 
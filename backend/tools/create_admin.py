# backend/tools/create_admin.py

from app.db import SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash


ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "123456789"
ADMIN_NAME = "Admin"


def main():
    db = SessionLocal()

    # 检查是否存在
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if user:
        print("👑 管理员已存在:", user.email)
        return

    # 创建管理员
    admin = User(
        email=ADMIN_EMAIL,
        hashed_password=get_password_hash(ADMIN_PASSWORD),
        full_name=ADMIN_NAME,
        role="admin",
        is_active=True,
    )

    db.add(admin)
    db.commit()

    print("🎉 管理员创建成功！")
    print(f"邮箱: {ADMIN_EMAIL}")
    print(f"密码: {ADMIN_PASSWORD}")


if __name__ == "__main__":
    main()

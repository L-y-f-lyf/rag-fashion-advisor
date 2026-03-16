# 直接测试注册 API
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag_project'))

# 手动测试
from database import SessionLocal, init_db
from models import User
from auth import get_password_hash

# 初始化数据库
init_db()

# 测试注册逻辑
db = SessionLocal()
try:
    # 检查用户名是否存在
    username = "testuser123"
    password = "testpass123"

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"用户 {username} 已存在")
        db.delete(existing_user)
        db.commit()
        print(f"已删除旧用户，请重试注册")
    else:
        # 创建新用户
        hashed_password = get_password_hash(password)
        print(f"密码哈希成功：{hashed_password}")

        new_user = User(username=username, password_hash=hashed_password)
        db.add(new_user)
        db.commit()
        print(f"用户创建成功！ID: {new_user.id}")
finally:
    db.close()
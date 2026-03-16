# 测试登录 API
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag_project'))

from database import SessionLocal, init_db
from models import User
from auth import get_password_hash, verify_password, create_access_token

# 初始化数据库
init_db()
db = SessionLocal()

try:
    # 先创建一个测试用户
    username = "testuser"
    password = "testpass"

    # 检查用户是否存在
    user = db.query(User).filter(User.username == username).first()
    if not user:
        # 创建测试用户
        hashed = get_password_hash(password)
        print(f"创建用户 {username}，密码哈希：{hashed}")
        user = User(username=username, password_hash=hashed)
        db.add(user)
        db.commit()
        print("用户创建成功")
    else:
        print(f"用户 {username} 已存在")

    # 测试登录
    print("\n--- 测试登录 ---")
    user = db.query(User).filter(User.username == username).first()
    print(f"找到用户：{user.username}")

    # 验证密码
    is_valid = verify_password(password, user.password_hash)
    print(f"密码验证结果：{is_valid}")

    # 创建 token
    if is_valid:
        token = create_access_token(data={"sub": user.username})
        print(f"Token: {token[:50]}...")

finally:
    db.close()
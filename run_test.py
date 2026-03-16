"""
测试并启动服务器
"""
import sys
import os
import traceback

# 添加路径
BASE_DIR = os.path.join(os.path.dirname(__file__), 'rag_project')
sys.path.insert(0, BASE_DIR)

print("=" * 50)
print("测试导入...")

try:
    print("1. 导入 database...")
    from database import init_db
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")
    traceback.print_exc()

try:
    print("2. 导入 auth...")
    import auth
    print(f"   OK - password hash: {auth.hash_password('test')[:30]}...")
except Exception as e:
    print(f"   FAIL: {e}")
    traceback.print_exc()

try:
    print("3. 导入 routers...")
    from routers import auth_router, chat_router, knowledge_router
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")
    traceback.print_exc()

try:
    print("4. 导入 main app...")
    from main import app
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")
    traceback.print_exc()

print("=" * 50)
print("启动服务器...")
print("访问：http://127.0.0.1:8000")
print("API 文档：http://127.0.0.1:8000/docs")
print("=" * 50)

import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000)

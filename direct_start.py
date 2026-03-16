# 启动脚本 - 直接运行
import sys
import os

# 添加 rag_project 到路径
project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rag_project')
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("测试导入...")

try:
    from database import init_db
    print("database: OK")
except Exception as e:
    print(f"database: FAIL - {e}")

try:
    import auth
    print(f"auth: OK - hash={auth.hash_password('test')[:20]}...")
except Exception as e:
    print(f"auth: FAIL - {e}")

try:
    from routers.auth import router as auth_router
    print("routers.auth: OK")
except Exception as e:
    print(f"routers.auth: FAIL - {e}")

try:
    from main import app
    print("main: OK")
except Exception as e:
    print(f"main: FAIL - {e}")

print("=" * 50)
print("启动服务器 http://127.0.0.1:8000")
print("=" * 50)

import uvicorn
from main import app
uvicorn.run(app, host="127.0.0.1", port=8000)

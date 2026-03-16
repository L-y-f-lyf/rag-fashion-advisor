# 测试路由导入
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag_project'))

print("开始测试导入...")

try:
    print("1. 测试导入 auth 模块...")
    from auth import get_password_hash, verify_password
    print("   ✓ auth 模块导入成功")
except Exception as e:
    print(f"   ✗ auth 模块导入失败：{e}")
    import traceback
    traceback.print_exc()

try:
    print("2. 测试导入 r"
          "outers 模块...")
    from routers import auth_router
    print("   ✓ auth_router 导入成功")
except Exception as e:
    print(f"   ✗ auth_router 导入失败：{e}")
    import traceback
    traceback.print_exc()

try:
    print("3. 测试导入 main 应用...")
    from main import app
    print("   ✓ app 导入成功")
except Exception as e:
    print(f"   ✗ app 导入失败：{e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")
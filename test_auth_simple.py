import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag_project'))

print("开始测试 auth 模块...")

try:
    from auth import get_password_hash, verify_password
    print("✓ auth 模块导入成功")
except Exception as e:
    print(f"✗ auth 模块导入失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试密码哈希
pwd = "test123"
print(f"\n测试密码：{pwd}")

try:
    hashed = get_password_hash(pwd)
    print(f"✓ 密码哈希成功：{hashed}")
except Exception as e:
    print(f"✗ 密码哈希失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试密码验证
try:
    result = verify_password(pwd, hashed)
    print(f"✓ 密码验证结果：{result}")
except Exception as e:
    print(f"✗ 密码验证失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n所有测试通过！")
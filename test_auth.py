# 测试认证模块
import sys
sys.path.insert(0, 'rag_project')

from auth import get_password_hash, verify_password

# 测试密码哈希
password = "testpass123"
hashed = get_password_hash(password)
print(f"原始密码：{password}")
print(f"哈希后：{hashed}")
print(f"验证结果：{verify_password(password, hashed)}")
print(f"错误密码验证：{verify_password('wrongpass', hashed)}")
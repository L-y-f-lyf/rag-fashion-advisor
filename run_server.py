"""
直接启动服务器 - 跳过所有复杂逻辑
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag_project'))

# 测试 auth 模块
print("测试 auth 模块...")
from auth import get_password_hash, verify_password
hashed = get_password_hash("test123")
print(f"密码哈希测试成功：{hashed[:40]}...")

# 启动服务器
print("\n启动服务器...")
import uvicorn
from main import app

uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
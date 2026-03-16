# 启动服务器
import uvicorn
import os
import sys

# 添加项目路径
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rag_project')
sys.path.insert(0, BASE_DIR)

from rag_project.main import app

if __name__ == "__main__":
    print("=" * 50)
    print("启动服务器...")
    print("访问：http://127.0.0.1:8000")
    print("API 文档：http://127.0.0.1:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)

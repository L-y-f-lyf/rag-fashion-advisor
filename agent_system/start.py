#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================== 穿搭智能顾问 Agent 系统 - 启动脚本 ====================

import os
import sys
import uvicorn
from pathlib import Path

# 确保在正确的目录运行
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 60)
print("👔 穿搭智能顾问 Agent 系统")
print("=" * 60)
print(f"工作目录：{script_dir}")
print("")

def check_chroma_db():
    """检查 Chroma 向量数据库是否存在"""
    chroma_path = script_dir / "chroma_db"
    if not chroma_path.exists():
        print("=" * 60)
        print("⚠️  警告：Chroma 向量数据库不存在！")
        print("=" * 60)
        print(f"预期路径：{chroma_path}")
        print("")
        print("请确保向量数据库已创建。")
        print("按 Enter 键继续启动（RAG 功能将受限）...")
        input()
        return False
    return True


def check_api_key():
    """检查 API Key 是否配置了"""
    try:
        from config import DASHSCOPE_API_KEY
        if DASHSCOPE_API_KEY == "你的API密钥" or not DASHSCOPE_API_KEY:
            print("=" * 60)
            print("⚠️  警告：未配置通义千问 API Key！")
            print("=" * 60)
            print("")
            print("请配置 API Key 后才能使用系统。您有以下几种方式：")
            print("")
            print("方式1：在 config.py 中直接修改 DASHSCOPE_API_KEY")
            print("方式2：创建 .env 文件，添加：DASHSCOPE_API_KEY=你的密钥")
            print("方式3：在启动后通过前端界面输入 API Key")
            print("")
            print("按 Enter 键继续启动（请在界面中输入 API Key）...")
            input()
            return False
        print(f"✓ API Key 已配置：{DASHSCOPE_API_KEY[:10]}...")
        return True
    except ImportError:
        print("⚠️  无法导入 config 模块")
        return False


def main():
    """主函数"""
    # 检查 Chroma 数据库
    check_chroma_db()

    # 检查 API Key
    check_api_key()

    print("")
    print("=" * 60)
    print("正在启动系统...")
    print("=" * 60)
    print("")

    # 导入配置
    try:
        import config
        HOST = config.HOST
        PORT = config.PORT
    except ImportError as e:
        print(f"导入配置失败：{e}")
        print("请确保 config.py 文件存在")
        return

    # 启动服务器
    print(f"📡 服务器地址：http://{HOST}:{PORT}")
    print(f"📄 API 文档：http://{HOST}:{PORT}/docs")
    print(f"🌐 前端页面：http://{HOST}:{PORT}/")
    print("")
    print("按 Ctrl+C 停止服务器")
    print("")

    try:
        uvicorn.run(
            "main:app",
            host=HOST,
            port=PORT,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"\n启动失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

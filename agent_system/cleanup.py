#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""清理临时文件，只保留核心项目文件"""

import os
import shutil

# 当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# 需要保留的核心文件
KEEP_FILES = [
    # 核心代码
    'config.py',
    'main.py',
    'agent.py',
    'tools.py',
    'start.py',
    '__init__.py',

    # 依赖和配置
    'requirements.txt',
    '.env.example',
    '.gitignore',

    # 文档
    'README.md',

    # 静态文件目录
    'static',

    # 数据库目录
    'chroma_db',
]

# 需要删除的文件/目录模式
DELETE_PATTERNS = [
    'test_*.py',
    'check_*.py',
    'fix_*.py',
    'install_*.py',
    'clean_*.py',
    'do_install.py',
    'diagnose.py',
    'simple_start.py',
    'verify_*.py',
    'quick_test.py',
    'run_test.py',
    'minimal.py',
    'ULTIMATE_FIX.py',
    'start_venv.py',
    'patch_langchain.py',

    '*.bat',
    '*.txt',
    '*.log',

    '__pycache__',
    '*.pyc',
]

print("="*60)
print("开始清理项目目录...")
print("="*60)

deleted_count = 0

# 删除匹配的文件
for pattern in DELETE_PATTERNS:
    if '*' in pattern:
        # 通配符模式
        import glob
        for filepath in glob.glob(pattern):
            if os.path.isfile(filepath) and filepath not in KEEP_FILES:
                print(f"删除文件: {filepath}")
                os.remove(filepath)
                deleted_count += 1
            elif os.path.isdir(filepath):
                print(f"删除目录: {filepath}")
                shutil.rmtree(filepath)
                deleted_count += 1
    else:
        # 精确匹配
        if os.path.exists(pattern):
            if os.path.isfile(pattern) and pattern not in KEEP_FILES:
                print(f"删除文件: {pattern}")
                os.remove(pattern)
                deleted_count += 1
            elif os.path.isdir(pattern) and pattern not in KEEP_FILES:
                print(f"删除目录: {pattern}")
                shutil.rmtree(pattern)
                deleted_count += 1

print("\n" + "="*60)
print(f"清理完成！共删除 {deleted_count} 个文件/目录")
print("="*60)
print("\n保留的核心文件:")
for f in sorted(os.listdir('.')):
    if not f.startswith('.') or f in KEEP_FILES:
        print(f"  - {f}")
import subprocess
import time
import sys
import os

os.chdir(r'C:\Users\yafei\PycharmProjects\PythonProject1')

print('Starting server...')
sys.stdout.flush()

proc = subprocess.Popen(
    ['C:/Users/yafei/AppData/Local/Programs/Python/Python312/python.exe', 'simple_server.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

time.sleep(5)

# 测试健康检查
import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5) as resp:
        print(f'Health check: {resp.read().decode()}')
except Exception as e:
    print(f'Health check failed: {e}')

# 测试注册
try:
    data = b'{"username": "test123", "password": "pass123"}'
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/auth/register',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f'Status: {resp.status}')
        print(f'Response: {resp.read().decode()}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    print(f'Response: {e.read().decode()}')
except Exception as e:
    print(f'Error: {e}')

proc.terminate()
proc.wait(timeout=5)
print('\\nServer logs:')
print(proc.stdout.read())
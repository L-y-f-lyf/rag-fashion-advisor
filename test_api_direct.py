# 直接测试 API
import requests

# 测试注册
url = "http://127.0.0.1:8000/api/auth/register"
data = {"username": "newuser123", "password": "pass123"}

print("=== 测试注册 ===")
try:
    resp = requests.post(url, json=data, timeout=5)
    print(f"状态码：{resp.status_code}")
    print(f"响应内容：{resp.text}")
except Exception as e:
    print(f"请求失败：{e}")

# 测试登录
url = "http://127.0.0.1:8000/api/auth/login"
data = {"username": "newuser123", "password": "pass123"}

print("\n=== 测试登录 ===")
try:
    resp = requests.post(url, json=data, timeout=5)
    print(f"状态码：{resp.status_code}")
    print(f"响应内容：{resp.text}")
except Exception as e:
    print(f"请求失败：{e}")
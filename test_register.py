# 测试注册 API
import requests

url = "http://127.0.0.1:8000/api/auth/register"
data = {"username": "testuser123", "password": "testpass123"}

try:
    response = requests.post(url, json=data)
    print(f"状态码：{response.status_code}")
    print(f"响应内容：{response.text}")
    print(f"响应头：{dict(response.headers)}")
except Exception as e:
    print(f"请求失败：{e}")
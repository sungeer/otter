import requests

url = "http://127.0.0.1:8000/messages"
data = {
    "content": "你好，这是一个测试消息",
    "sender": "user"
}

response = requests.post(url, json=data)

print("状态码：", response.status_code)
print("响应内容：", response.text)

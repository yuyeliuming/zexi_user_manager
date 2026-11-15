#测试注册时抢注情况(AI生成)
import threading
import requests

url = "http://127.0.0.1:8000/auth/register"
payload = {"username": "race_test1", "password": "123"}

def register():
    response = requests.post(url, json=payload)
    print(f"状态码: {response.status_code}, 返回: {response.json()}")

# 同时启动 5 个线程去抢注
threads = []
for i in range(5):
    t = threading.Thread(target=register)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
import sqlite3

# 连接数据库
conn = sqlite3.connect("user.db")
cursor = conn.cursor()

# 查询所有数据
cursor.execute("SELECT id, username, password FROM users")
users = cursor.fetchall()

print("--- 当前数据库里的用户 ---")
for user in users:
    print(f"ID: {user[0]}, 用户名: {user[1]}, 密码(哈希): {user[2][:20]}...")
print("--------------------------")

conn.close()
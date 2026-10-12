from fastapi import FastAPI,HTTPException,Header
from pydantic import BaseModel
from database import init_db
import sqlite3
import uuid
app=FastAPI()
sessions ={}
init_db()
class UserAuth(BaseModel):
    username: str
    password: str
class UsernameUpdate(BaseModel):
    new_username: str
class PasswordUpdate(BaseModel):
    new_password: str
#----------------------------------用户注册-------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
@app.post("/auth/register",status_code=201)
def register(data: UserAuth):
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT*FROM users WHERE username = ?",(data.username,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        raise HTTPException(status_code=409, detail="User already exists")
    cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",(data.username,data.password))
    conn.commit()
    conn.close()
    return {"message": "User created successfully","username": data.username}
#---------------------------用户登录---------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
@app.post("/auth/login")
def login(data:UserAuth):
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",(data.username,data.password))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    session_id = str(uuid.uuid4())
    user_id =user[0]
    sessions[session_id] = user_id

    return {"sessionId": session_id, "message": "login success"}
#----------------------------------查看用户信息-----------------------------------------------------------
#------------------------------------------------------------------------------------------------------
@app.get("/users/me")
def get_current_user(session_id:str = Header(None)):
    if not session_id:
        raise HTTPException(status_code=401,detail="unauthorized")

    user_id= sessions.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401,detail="unauthorized")
    conn =sqlite3.connect("user.db")
    cursor =conn.cursor()
    cursor.execute("SELECT id,username FROM users WHERE id = ?",(user_id,))
    user = cursor.fetchone()
    conn.close()
    return{"id":user[0],"username":user[1]}
#-------------------------------------查看用户列表----------------------------------------------------
#----------------------------------------------------------------------------------------------------
@app.get("/users")
def get_all_users(session_id:str = Header(None)):
    if not session_id:
        raise HTTPException(status_code=401,detail="unauthorized")
    user_id= sessions.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401,detail="unauthorized")
    conn =sqlite3.connect("user.db")
    cursor =conn.cursor()
    cursor.execute("SELECT id,username FROM users")
    users = cursor.fetchall()
    conn.close()
    return[{"id":user[0],"username":user[1]} for user in users]
#--------------------------------------修改用户名------------------------------------------------------
#----------------------------------------------------------------------------------------------------
@app.patch("/users/me/username")
def update_username(data:UsernameUpdate,session_id:str = Header(None)):
    if not session_id:
        raise HTTPException(status_code=401,detail="unauthorized")
    user_id = sessions.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    conn =sqlite3.connect("user.db")
    cursor =conn.cursor()
    #查询重名的思路问了deepseek
    cursor.execute("SELECT * FROM users WHERE name = ?",(data.new_username))
    user = cursor.fetchone()
    if user:
        conn.close()
        raise HTTPException(status_code=409, detail="User already exists")

    cursor.execute("UPDATE users SET username = ? WHERE id =?",(data.new_username,user_id))
    conn.commit()
    #没想出来“操作不存在的用户”是什么情况，就咨询了一下deepseek
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User does not exist")
    # 上一步的情况蛮刁钻的，两个设备先登录同一个账号，一个先注销账号，另一个再去改名，自然就“用户不存在”
    conn.close()
    return {"message": "User updated successfully","username": data.new_username}
#----------------------------------修改用户密码----------------------------------------------------------
#------------------------------------------------------------------------------------------------------
@app.patch("/users/me/password")
def update_password(data:PasswordUpdate,session_id:str = Header(None)):
    if not session_id:
        raise HTTPException(status_code=401,detail="unauthorized")
    user_id = sessions.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    conn =sqlite3.connect("user.db")
    cursor =conn.cursor()
    cursor.execute("UPDATE users SET password =? WHERE id = ?",(data.new_password,user_id))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User does not exist")
    conn.close()
    return {"message": "Password updated successfully"}
#-----------------------------------注销账号-------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
@app.delete("/users/me")
def delete_user(session_id:str = Header(None)):
    if not session_id:
        raise HTTPException(status_code=401,detail="unauthorized")
    user_id = sessions.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    conn =sqlite3.connect("user.db")
    cursor =conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?",(user_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User does not exist")
    conn.close()
    return {"message": "Account deleted successfully"}


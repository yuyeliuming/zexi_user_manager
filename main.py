import sqlite3
from fastapi import FastAPI,HTTPException,Header,Depends
from database import init_db,hash_password,verify_password
from schemas import UserAuth,UsernameUpdate,PasswordUpdate,Token
from security import create_access_token,get_current_user_id
from logger import logger

#实例化FastAPI应用
app=FastAPI()
init_db()

#用户注册
@app.post("/auth/register",status_code=201)
def register(data: UserAuth):
    conn = sqlite3.connect("user.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT*FROM users WHERE username = ?",(data.username,))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            logger.warning("%s already exist", data.username)
            raise HTTPException(status_code=409, detail="User already exists")
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",
                       (data.username,hash_password(data.password)))
        conn.commit()
        logger.info("creat successfully | username=%s",data.username)
        return {"message": "User created successfully",
                "username": data.username}
    #防竞态条件
    except sqlite3.IntegrityError:
        conn.rollback()
        logger.warning("%s already exist", data.username)
        raise HTTPException(status_code=409, detail="User already exists")
    finally:
        conn.close()


#用户登录
@app.post("/auth/login",response_model=Token)
def login(data:UserAuth):
    conn = sqlite3.connect("user.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?",(data.username,))
        user = cursor.fetchone()
        if not user or not verify_password(data.password, user[2]):
            logger.warning("Invalid username or password | username=%s",data.username)
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        token=create_access_token(user[0])
        logger.info ("login successfully | user_id=%s username=%s",user[0],user[1])
        return{"access_token":token,
               "token_type":"bearer"}
    finally:
        conn.close()


#查看用户信息
@app.get("/users/me")
def get_me(user_id:int =Depends(get_current_user_id)):
    conn = sqlite3.connect("user.db")
    try:
        cursor =conn.cursor()
        cursor.execute("SELECT id,username FROM users WHERE id = ?",(user_id,))
        user = cursor.fetchone()
        if not user:
            logger.warning("User has been deleted | user_id=%s", user_id)
            raise HTTPException(status_code=404, detail="User does not exist")
        logger.info("get user info successfully | user_id=%s",user_id)
        return{"id":user[0],
               "username":user[1]}
    finally:
        conn.close()


#查看用户列表
@app.get("/users")
def get_all_users(user_id:int =Depends(get_current_user_id)):
    conn =sqlite3.connect("user.db")
    try:
        cursor =conn.cursor()
        cursor.execute("SELECT id,username FROM users")
        users = cursor.fetchall()
        logger.info("get all users successfully | user_id=%s",user_id)
        return[{"id":user[0],"username":user[1]} for user in users]
    finally:
        conn.close()


#修改用户名
@app.patch("/users/me/username")
def update_username(data:UsernameUpdate,user_id:int =Depends(get_current_user_id)):
    conn = sqlite3.connect("user.db")
    try:
        cursor =conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND id !=?",
                       (data.new_username,user_id))
        if cursor.fetchone():
            logger.warning("%s already exist",data.new_username)
            raise HTTPException(status_code=409, detail="User already exists")

        cursor.execute("UPDATE users SET username = ? WHERE id =?",
                       (data.new_username,user_id))

        # 防止两个设备先登录同一个账号，一个先注销账号，另一个再去改名
        if cursor.rowcount == 0:
            conn.rollback()
            logger.warning("User has been deleted | user_id=%s",user_id)
            raise HTTPException(status_code=404, detail="User does not exist")
        conn.commit()
        logger.info ("update successfully | user_id=%s new_username=%s",user_id,data.new_username)
        return {"message": "Username updated successfully",
                "username": data.new_username}
    #防竞态条件
    except sqlite3.IntegrityError:
        conn.rollback()
        logger.warning("%s already exist",data.new_username)
        raise HTTPException(status_code=409, detail="User already exists")
    finally:
        conn.close()


#修改用户密码
@app.patch("/users/me/password")
def update_password(data:PasswordUpdate,user_id:int =Depends(get_current_user_id)):
    conn = sqlite3.connect("user.db")
    try:
        cursor =conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id =?",
                       (user_id,))
        user = cursor.fetchone()
        #防并发
        if not user:
            logger.warning("User has been deleted | user_id=%s",user_id)
            raise HTTPException(status_code=404, detail="User does not exist")
        if not verify_password(data.old_password,user[0]):
            logger.warning("Incorrect password | user_id=%s",user_id)
            raise HTTPException(status_code=400, detail="Incorrect password")
        cursor.execute("UPDATE users SET password = ? WHERE id = ?",
                       (hash_password(data.new_password),user_id))

        if cursor.rowcount == 0:
            conn.rollback()
            logger.warning("User has been deleted | user_id=%s",user_id)
            raise HTTPException(status_code=404, detail="User does not exist")
        conn.commit()
        logger.info("update successfully | user_id=%s",user_id)
        return {"message": "Password updated successfully"}
    finally:
        conn.close()

#注销账号
@app.delete("/users/me")
def delete_user(user_id:int =Depends(get_current_user_id)):
    conn = sqlite3.connect("user.db")
    try:
        cursor =conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?",(user_id,))
        if cursor.rowcount == 0:
            conn.rollback()
            logger.warning("User has been deleted | user_id=%s",user_id)
            raise HTTPException(status_code=404, detail="User does not exist")
        conn.commit()
        logger.info("delete successfully | user_id=%s",user_id)
        return {"message": "Account deleted successfully"}
    finally:
        conn.close()


import jwt
import os
import sqlite3
from logger import logger
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException,Header,Depends
from datetime import datetime,timedelta,timezone
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

load_dotenv()
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY 未配置，请检查 .env")
ALGORITHM = "HS256"
EXP_MINUTES = 120

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(user_id:int) -> str:
    token_expires = datetime.now(timezone.utc) + timedelta(minutes=EXP_MINUTES)
    payload ={
        "exp": token_expires,
        "sub": str(user_id),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id(cred:HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) ->int:
    if cred is None:
        logger.warning("Missing token")
        raise HTTPException(status_code=401,detail="Missing token")
    token = cred.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning("Invalid token: missing user id")
            raise HTTPException(status_code=401,detail="Invalid token")
        try:
            user_id = int(user_id)
        except ValueError:
            logger.warning("Invalid user id format in token: %s", user_id)
            raise HTTPException(status_code=401, detail="Invalid user id format")
        conn=sqlite3.connect("user.db")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id=?",(user_id,))
            user = cursor.fetchone()
        finally:
            conn.close()
        if not user:
            logger.warning("User not found for user_id: %s", user_id)
            raise HTTPException(status_code=404,detail="Account has been deleted")
        return user_id
        #单独处理token过期，子类在父类前面
    except jwt.ExpiredSignatureError:
        logger.warning("Token is expired")
        raise HTTPException(status_code=401,detail="token is expired")
    #处理格式错误、签名错误等jwt抛出异常等
    except InvalidTokenError:
        logger.warning("Invalid token")
        raise HTTPException(status_code=401,detail="Invalid token")




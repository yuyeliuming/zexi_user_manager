import sqlite3
import hashlib
import secrets
import hmac
from logger import logger
def init_db():
    try:
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Error initializing database: %s", str(e),exc_info=True)
        raise
    finally:
        conn.close()
    
def hash_password(password:str)-> str:
    # 1 生成哈希盐
    salt =secrets.token_hex(16)
    # 2 计算哈希
    hashed=hashlib.pbkdf2_hmac('sha256',
                               password.encode('utf-8'),
                               salt.encode('utf-8'),
                               200000).hex()
    return(f'{salt}${hashed}')
def verify_password(input_password:str,stored_password:str)-> bool:
    try:
        salt,old_hashed=stored_password.split('$')
        new_hashed = hashlib.pbkdf2_hmac('sha256',
                                 input_password.encode('utf-8'),
                                 salt.encode('utf-8'),
                                 200000).hex()
        #防止被利用时间差
        return hmac.compare_digest(old_hashed,new_hashed)
    except Exception as e:
        logger.error("Error verifying password: %s", str(e),exc_info=True)
        return False




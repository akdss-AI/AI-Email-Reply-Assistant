from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi import Depends , HTTPException ,status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from fastapi.security import OAuth2PasswordBearer
oauth2_schema=OAuth2PasswordBearer(tokenUrl='login')
load_dotenv()
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
pwd_context=CryptContext(
    schemes=['bcrypt'],
    deprecated='auto'
)
def hash_password(password:str):
    return pwd_context.hash(password)
def verify_password(plain_password:str , hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)
def create_access_token(data:dict):
    to_encode= data.copy()
    expire=datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,
                SECRET_KEY,
                  algorithm=ALGORITHM)
def verify_access_token(token:str):
    try:
        payload=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except Exception as e:
        print("JWT ERROR:",e)
        return None
def get_current_user(
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db)
):
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
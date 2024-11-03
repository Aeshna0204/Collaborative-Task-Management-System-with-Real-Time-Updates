from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import timedelta, datetime
from app.config import SECRET_KEY, ALGORITHM
from app.database import get_db
from app.schemas import UserCreate
from sqlalchemy.orm import Session
from app.models import User
from app.dependencies import oauth2_scheme
import bcrypt
from passlib.context import CryptContext
import traceback

import logging


router = APIRouter()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)






@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if the user already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered.")
        
        # Hash the password and create a new user
        hashed_password = hash_password(user_data.password)
        new_user = User(username=user_data.username, password_hash=hashed_password, role=user_data.role)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "User registered successfully", "user_id": new_user.id}
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Detailed error traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Include role in the token payload
    token_data = {"sub": str(user.id), "role": user.role}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Encoded access token: {token}")
    return {"access_token": token, "token_type": "bearer"}


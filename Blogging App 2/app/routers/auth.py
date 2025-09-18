from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserResponse, UserCreate, Token
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from typing import Annotated
from app.auth_utils import get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from datetime import timedelta

router = APIRouter(tags=['authentication'])

db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: db_dependency):
    # check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is not None:
        raise HTTPException(detail="Email already registered", status_code=status.HTTP_400_BAD_REQUEST)
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user is not None:
        raise HTTPException(detail="Email already registered", status_code=status.HTTP_400_BAD_REQUEST)
    
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return db_user

@router.get("/test-auth")
async def test_auth():
    return {"message": "Auth endpoint is working"}

@router.post('/login', response_model=Token)
async def login(username: str, password: str, db: db_dependency):
    print("hi")
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": 'bearer'}
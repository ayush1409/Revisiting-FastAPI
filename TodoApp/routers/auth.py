from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import User
from passlib.context import CryptContext
from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


SECRET_KEY='443e6a0ac87aec0cf5c0b1c5ea08dbcf8911fbfdb9b45d056a32597838d3e450'
ALGORITHM='HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a common database dependency to inject everywhere needed
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(user_name: str, password: str, db):
    user = db.query(User).filter(User.user_name == user_name).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, user_role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': user_role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        userid: str = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or userid is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': userid, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

class Token(BaseModel):
    access_token: str
    token_type: str

class CreateUserRequest(BaseModel):
    email: str
    user_name: str
    first_name: str
    last_name: str
    password: str
    is_active: bool
    role: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = User(
        email = create_user_request.email,
        user_name = create_user_request.user_name,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        is_active = True,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password)
    )

    db.add(create_user_model)
    db.commit()

@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def get_token(db: db_dependency,auth_form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(auth_form.username, auth_form.password, db)
    if not user:
        print(f"{auth_form.username}, {auth_form.password}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.user_name, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
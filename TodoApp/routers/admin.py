from typing import Annotated, Optional
from fastapi import Depends, APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Todos, User
from database import SessionLocal, engine
from routers.auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a common database dependency to inject everywhere needed
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todo(user: user_dependency, db: db_dependency):
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to list all todos")
    return db.query(Todos).all()

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: str = Path(gt=0)):
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to remove todo")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
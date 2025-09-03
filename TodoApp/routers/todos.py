from typing import Annotated, Optional
from fastapi import Depends, APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Todos, User
from database import SessionLocal, engine
from routers.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a common database dependency to inject everywhere needed
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

class TodoRequest(BaseModel):
    id: Optional[int] = Field(description="ID not needed when creating Todo", default=None)
    title: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Learn Python",
                "description": "Complete all Tutorials",
                "priority": 5,
                "complete": False
            }
        }
    }



@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todo(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    user_todos = db.query(Todos).filter(Todos.owner == user.get('id')).all()
    return user_todos

@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner == user.get('id')).first()
    # We are using .first() because we know that id is unique, thus optimizing by not searching after
    # finding the first record

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = Todos(**todo_request.model_dump(), owner=user.get('id'))
    db.add(todo_model)
    db.commit()

@router.put("/todos", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency ,db: db_dependency, 
                      todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_request.id).filter(Todos.owner == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo_model)
    db.commit()
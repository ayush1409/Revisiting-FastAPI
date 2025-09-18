from fastapi import APIRouter, Depends, HTTPException, status, Path
from app.schemas.blog import BlogResponse, BlogCreate, BlogUpdate
from app.database import get_db
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.models.user import User
from app.models.blog import Blog
from app.auth_utils import get_current_user
from datetime import datetime

router = APIRouter(prefix='/blogs', tags=['blogs'])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

# Create Blog Endpoint
@router.post("/", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
async def create_blog(blog: BlogCreate, db: db_dependency, current_user: user_dependency):
    published_date = datetime.now() if not blog.is_draft else None

    db_blog = Blog(
        title = blog.title,
        content = blog.content,
        is_draft = blog.is_draft,
        published_at = published_date,
        author_id = current_user.id
    )

    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog

@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(db: db_dependency, current_user: user_dependency, blog_id: int = Path(gt=0)):
    db_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not db_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found!")
    
    # show only non-published blogs to other users
    if db_blog.is_draft and db_blog.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found!")
    
    return db_blog
    

@router.put("/{blog_id}", response_model=BlogResponse, status_code=status.HTTP_200_OK)
async def update_model(blog: BlogUpdate, db: db_dependency, current_user: user_dependency, blog_id: int = Path(gt=0)):
    db_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not db_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found!")
    
    if current_user.id != db_blog.author_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised to edit this blog")
    
    if blog.title is not None:
        db_blog.title = blog.title
    
    if blog.content is not None:
        db_blog.content = blog.content
    if blog.is_draft is not None:
        db_blog.is_draft = blog.is_draft
        # Update published_at based on draft status
        if not blog.is_draft and not db_blog.published_at:
            blog.published_at = datetime.now()
    db.commit()
    db.refresh(db_blog)
    return db_blog


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_blog(db: db_dependency, current_user: user_dependency, blog_id: int = Path(gt=0)):
    db_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not db_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog does not exists!")
    
    if current_user.id != db_blog.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorised to delete this blog")
    
    db.delete(db_blog)
    db.commit()
    return {"message": "Blog deleted successfully!"}

@router.get("/user/me", response_model=List[BlogResponse], status_code=status.HTTP_200_OK)
async def get_user_blogs(db: db_dependency, current_user: user_dependency):
    blogs = db.query(Blog).filter(Blog.author_id == current_user.id).first()
    return blogs
from fastapi import FastAPI, status
from app.database import Base, engine
from app.routers import auth, blogs

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Blogging App')

app.include_router(auth.router, prefix='/auth', tags=['authenticated'])
app.include_router(blogs.router, tags=["blogs"])

@app.get('/health', status_code=status.HTTP_200_OK)
async def health_check():
    return {"message": "healthy"}
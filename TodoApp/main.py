
from fastapi import FastAPI, status
from routers import auth, todos, admin
import models
from database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get("/healthy", status_code=status.HTTP_200_OK)
async def check_health():
    return {'status': 'Healthy'}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
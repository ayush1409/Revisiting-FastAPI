from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from models import Todos

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingLocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingLocalSession()
    try: 
        yield db
    except: 
        db.close()

def override_get_current_user():
    return {'username': 'codingwithayush', 'id': 1, 'role': 'admin'}


client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(
        id = 1,
        title = 'Learn Python',
        description = 'Learn everyday',
        priority = 5,
        complete = False,
        owner = 1
    )
    db = TestingLocalSession()
    db.add(todo)
    db.commit()
    yield todo

    # After testing, clear the testing db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()
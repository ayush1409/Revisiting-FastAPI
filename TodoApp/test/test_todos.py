from main import app
from routers.todos import get_db, get_current_user
from fastapi import status
from models import Todos
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_all_todos(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': 1,
        'title': 'Learn Python',
        'description': 'Learn everyday',
        'priority': 5,
        'complete': False,
        'owner': 1
    }]

def test_get_todo_success(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'title': 'Learn Python',
        'description': 'Learn everyday',
        'priority': 5,
        'complete': False,
        'owner': 1
    }

# def test_get_todo_unsuccessful(test_todo):
#     response = client.get("/todos/999")
#     assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_todo(test_todo):
    request_json = {
        'title': 'Learn FastAPI',
        'description': 'Learn Backend everyday',
        'priority': 5,
        'complete': False,
        'owner': 1
    }
    response = client.post("/todos", json=request_json)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingLocalSession()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_json.get('title')
    assert model.description == request_json.get('description')
    assert model.complete == request_json.get('complete')
    assert model.owner == request_json.get('owner')
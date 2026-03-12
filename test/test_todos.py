from sqlalchemy import create_engine, text
from app.main import app
from app.routers.todos import get_db, get_current_user
# from app.routers.auth import get_current_user

from fastapi import status
from app.models import Todos
from test.utils import * #TestingSessionLocal, override_get_db, override_get_current_user, client, engine, test_todo

	
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
	response = client.get("/")
	# print(response.json())
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == [{
		'complete': False,
		'title': 'Learn to code!',
		'description': 'Need to learn everyday!',
		'id': 1,
		'priority': 5,
		'owner_id': 1
	}] 

def test_read_one_authenticated(test_todo):
	response = client.get("/todo/1")
	# print(response.json())
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == {
		'complete': False,
		'title': 'Learn to code!',
		'description': 'Need to learn everyday!',
		'id': 1,
		'priority': 5,
		'owner_id': 1
	}

def test_read_one_authenticated_not_found():
	response = client.get("/todo/999")
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo(test_todo, db_session):
	request_data={
		'title':'New Todo !',
		'description':'New todo description',
		'priority': 5,
		'complete': False,
	}

	response = client.post("/todo/", json=request_data)
	# print(response.json())
	assert response.status_code == status.HTTP_201_CREATED

	todos: Todos | None = db_session.query(Todos).filter(Todos.id == 2).first()

	# if todos:
	# 	print("Model found in database:")
	# 	print(todos.to_dict())
	# 	print("\n\n\n")
	# 	print("Request data:")
	# 	print(request_data)
	# Check if the model exists
	assert todos is not None, "Todo with id 2 was not created in the database"

	assert todos.title == request_data.get('title')
	assert todos.description == request_data.get('description')
	assert todos.priority == request_data.get('priority')
	assert todos.complete == request_data.get('complete')

def test_update_todo(test_todo, db_session):
	request_data = {
		'title':'Change the title of the todo already saved!',
		'description': 'Need to learn everyday!',
		'priority': 5,
		'complete': False,
	}

	response = client.put('todo/1', json=request_data)
	assert response.status_code == status.HTTP_204_NO_CONTENT
	model = db_session.query(Todos).filter(Todos.id == 1).first()
	assert model is not None, "Todo with id 1 was not found in the database after update"
	# print(f"model.title: {model.title}")
	assert model.title == request_data.get('title')
	assert model.description == request_data.get('description')
	assert model.priority == request_data.get('priority')
	assert model.complete == request_data.get('complete')

def test_update_todo_not_found(test_todo):
	request_data = {
		'title':'Change the title of the todo already saved!',
		'description': 'Need to learn everyday!',
		'priority': 5,
		'complete': False,
	}

	response = client.put('todo/999', json=request_data)
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {'detail': 'Todo not found.'}

def test_delete_todo(test_todo, db_session):
	response = client.delete('todo/1')
	assert response.status_code == status.HTTP_204_NO_CONTENT
	model = db_session.query(Todos).filter(Todos.id == 1).first()
	assert model is None, "Todo with id 1 was not deleted from the database"


def test_delete_todo_not_found(test_todo, db_session):
	response = client.delete('todo/999')
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {'detail': 'Todo not found.'}
	model = db_session.query(Todos).filter(Todos.id == 999).first()
	assert model is None, "Todo with id 999 does not exist in database"

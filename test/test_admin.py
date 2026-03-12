from test.utils import *
from app.routers.admin import get_db, get_current_user
from fastapi import status
from app.models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user	

def test_admin_read_all_authenticated(test_todo):
	response = client.get("/admin/todo")
	assert response.status_code == status.HTTP_200_OK
	print("\n\nResponse JSON:\n", response.json(), "\n\n")
	# print(response.json())
	assert response.json() == [{
		'complete': False,
		'title': "Learn to code!",
		'description': "Need to learn everyday!",
		'id': 1,
		'priority': 5,
		'complete': False,
		'owner_id': 1
	}]


def test_admin_delete_todo(test_todo, db_session):
	response = client.delete("/admin/todo/1")
	assert response.status_code == status.HTTP_204_NO_CONTENT

	model = db_session.query(Todos).filter(Todos.id == 1).first()
	assert model is None # its none because the record should be deleted

def test_admin_todo_not_found():
	response = client.delete("/admin/todo/999")
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {"detail": "Todo not found."}
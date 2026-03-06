from test.utils import *
from app.routers.users import get_db, get_current_user
from fastapi import status
from app.models import Users

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user	

def test_return_user(test_user):
	response = client.get("/users/user/")
	assert response.status_code == status.HTTP_200_OK
	print("\n\nResponse JSON:\n", response.json(), "\n\n")

	assert response.json()["username"] == 'hcorte'
	assert response.json()["email"] == 'hcorte@lnec.pt'
	assert response.json()["first_name"] == 'Henrique'
	assert response.json()["last_name"] == 'Corte'
	#assert response.json()["hashed_password"] == '$2b$12$dgIg2wU/mhaQ9hhFMU6JVeXXW4/lKUjIIiksZ0sB0Vw0DIWG1zhDq'  # bcrypt_context.hash('testpassword')
	assert response.json()["role"] == 'admin'
	assert response.json()["phone_number"] == '1234567890'
	assert response.json()["is_active"] == True

	# db = TestingSessionLocal()
	# model = db.query(Users).filter(Users.id == 1).first()
	# if model is not None:
	# 	print("\n\nModel:\n", model.to_dict(), "\n\n")
	# else:
	# 	print("\n\nModel not found.\n\n")
	# db.close()

def test_change_password_success(test_user):
	# to garantie that the id is 1 in the test_user fixture the database clean up needs RESTART IDENTITY CASCADE;" otherwise the id will be incremented and the test will fail because the user with id 1 will not be found
	response = client.put("/users/password/1", json={
		"password": "testpassword",
		"new_password":"newpassword"
	})
	db = TestingSessionLocal()
	model = db.query(Users).filter(Users.id == 1).first()
	if model is not None:
		print("\n\nModel:\n", model.to_dict(), "\n\n")
	else:
		print("\n\nModel not found.\n\n")
	db.close()
	#assert response.is_success
	assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_not_found(test_user):
	response = client.put("/users/password/999", json={
		"password": "testpassword",
		"new_password":"newpassword"
	})

	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	assert response.json() == {"detail": 'Authentication Failed'}

def test_change_password_wrong_password(test_user):
	response = client.put("/users/password/1", json={
		"password": "wrongpassword",
		"new_password":"newpassword"
	})

	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	assert response.json() == {"detail": 'Error on password change'}

def test_change_phone_number_success(test_user):
	response = client.put("/users/phone_number/1", json="9999999999")
	assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_phone_number_not_found(test_user):
	response = client.put("/users/phone_number/999", json="9999999999")
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {"detail": 'User not found.'}
from test.utils import *
from app.routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user, db_session):

	authenticated_user = authenticate_user(test_user.username, 'testpassword', db_session)
	assert authenticated_user is not None
	assert authenticated_user.username == test_user.username

	non_existing_user = authenticate_user('WrongUserName', 'testpassword', db_session)
	assert non_existing_user is None # not False since the function as been change to return nothing(None) since that more python oriented

	wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db_session)
	assert wrong_password_user is None # not False since the function as been change to return nothing(None) since that more python oriented

def test_create_access_token():
	username = 'testuser'
	user_id = 1
	role = 'user'
	expires_delta = timedelta(days=1)

	token = create_access_token(username=username, user_id=user_id, role=role, expires_delta=expires_delta)

	decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})

	assert decode_token['sub'] == username
	assert decode_token['id'] == user_id
	assert decode_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():

	encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
	token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

	user = await get_current_user(token=token)
	# print("user:\n", user)
	assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
	encode = {'role': 'user'}
	token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

	with pytest.raises(HTTPException) as excinfo:
		await get_current_user(token=token)

	assert excinfo.value.status_code == 401
	assert excinfo.value.detail == 'Could not validate user.'

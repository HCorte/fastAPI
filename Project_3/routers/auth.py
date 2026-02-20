from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
import starlette.status as status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt


router = APIRouter()

# generated from teh command: openssl rand -hex 32
SECRET_KEY = 'd7cd3fb6cd1b69980926a34d666fe676232a9514350b135446c9f563ab4f1431'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class CreateUserRequest(BaseModel):
	username: str
	email: str
	first_name: str
	last_name: str
	password: str
	role: str

class Token(BaseModel):
	access_token: str
	token_type: str


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

#db dependency injection
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
	user = db.query(Users).filter(Users.username == username).first()
	if not user:
		return False
	if not bcrypt_context.verify(password, user.hashed_password):
		return False
	return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
	print(f'username: {username} ::::: id: {user_id}')
	enconde = {'sub': username, 'id': user_id}
	print(enconde)
	print('\n\n\n\n')
	expires = datetime.now(timezone.utc) + expires_delta
	enconde.update({'exp': expires})
	return jwt.encode(enconde, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/auth/", status_code=status.HTTP_201_CREATED)
async def createUser(db: db_dependency,create_user_request: CreateUserRequest):
	create_user_model = Users(
		email=create_user_request.email,
		username=create_user_request.username,
		first_name=create_user_request.first_name,
		last_name=create_user_request.last_name,		 
		role=create_user_request.role,
		hashed_password=bcrypt_context.hash(create_user_request.password),
		is_active=True
	)

	db.add(create_user_model)
	db.commit()

	#return create_user_model

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
								 db: db_dependency):
	user = authenticate_user(form_data.username, form_data.password, db)
	print('\n\n\n')
	print(user.to_dict())
	print('\n\n\n')
	if not user:
		return 'Failed Authentication'
	
	print(user.id)
	token = create_access_token(user.username, user.id, timedelta(minutes=20))
	
	return {
		'access_token': token,
		'token_type': 'bearer'
	}
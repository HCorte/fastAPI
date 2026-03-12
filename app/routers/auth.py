from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
import starlette.status as status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt,JWTError
from typing import Optional

router = APIRouter(
	prefix='/auth',
	tags=['auth']
)

# generated from teh command: openssl rand -hex 32
SECRET_KEY = 'd7cd3fb6cd1b69980926a34d666fe676232a9514350b135446c9f563ab4f1431'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
	username: str
	email: str
	first_name: str
	last_name: str
	password: str
	role: str
	phone_number: str

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

def hash_password(password: str) -> str:
	return bcrypt_context.hash(password)

def authenticate_user(username: str, password: str, db) -> Users | None:
	user = db.query(Users).filter(Users.username == username).first()
	if not user:
		return 
	if not bcrypt_context.verify(password, user.hashed_password):
		return 
	return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
	return bcrypt_context.verify(plain_password, hashed_password)

def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
	enconde = {'sub': username, 'id': user_id, 'role': role}
	expires = datetime.now(timezone.utc) + expires_delta
	enconde.update({'exp': expires})
	return jwt.encode(enconde, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
		username: Optional[str] = payload.get('sub')
		user_id: Optional[int] = payload.get('id')
		user_role: Optional[str] = payload.get('role') 
		if username is None or user_id is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
					   detail='Could not validate user.')
		return {'username': username, 'id': user_id, 'user_role': user_role}
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
				detail='Could not validate user.')

@router.post("/", status_code=status.HTTP_201_CREATED)
async def createUser(db: db_dependency,create_user_request: CreateUserRequest):
	try:
		create_user_model = Users(
			email=create_user_request.email,
			username=create_user_request.username,
			first_name=create_user_request.first_name,
			last_name=create_user_request.last_name,		 
			role=create_user_request.role,
			hashed_password=bcrypt_context.hash(create_user_request.password),
			is_active=True,
			phone_number=create_user_request.phone_number
		)

		db.add(create_user_model)
		db.commit()
	
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail=f"Error creating user: {e}")

	return {
		'username': create_user_request.username,
		'email': create_user_request.email,
	}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
								 db: db_dependency):
	user = authenticate_user(form_data.username, form_data.password, db)
	# print('\n\n\n')
	# print(user.to_dict())
	# print('\n\n\n')
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
					   detail='Could not validate user.')
	
	# print(user.id)
	token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
	
	return {
		'access_token': token,
		'token_type': 'bearer'
	}
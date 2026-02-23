from fastapi import APIRouter,Depends, HTTPException, Path
from pydantic import BaseModel, Field
import starlette.status as status
from typing import Annotated
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Users
from database import SessionLocal
from .auth import get_current_user, hash_password

router = APIRouter(
	prefix='/users',
	tags=['users']
)

class UpdateUserPasswordRequest(BaseModel):
	#username: str
	password: str

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

#db dependency injection
db_dependency = Annotated[Session, Depends(get_db)]
# user dependency injection (token validation)
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
		user: user_dependency,
		db: db_dependency,
		user_id: int = Path(gt=0)
	):
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	user_model = db.query(Users).filter(Users.user_id == user_id)\
		.first()
	
	if user_model is not None:
		return user_model
	raise HTTPException(status_code=404, detail='User not found.')


@router.put("/user/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_password(
		user: user_dependency,
		db: db_dependency,
		update_user_password_request: UpdateUserPasswordRequest,
		user_id: int = Path(gt=0),
	):
	if user is None or user.get('id') != user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	#username = update_user_password_request.username
	password = update_user_password_request.password
	user_model = db.query(Users).filter(Users.id == user_id)\
		.first()
		#.filter(Users.username == username)\
	if user_model is None:
		raise HTTPException(status_code=404, detail='User not found.')
	
	# hash the new password and update the user model
	hashed_pass = hash_password(password)
	user_model.hashed_password = hashed_pass
	try:
		db.add(user_model)
		db.commit()
		db.refresh(user_model)
		return user_model
	except SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Database error while updating user password."
		)
	
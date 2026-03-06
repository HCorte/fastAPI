from fastapi import APIRouter,Depends, HTTPException, Path, Body
from pydantic import BaseModel, Field
import starlette.status as status
from typing import Annotated
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user, hash_password, verify_password

router = APIRouter(
	prefix='/users',
	tags=['users']
)

class UpdateUserPasswordRequest(BaseModel):
	password: str
	new_password: str = Field(min_length=6)

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

@router.get("/user/", status_code=status.HTTP_200_OK)
async def get_user(
		user: user_dependency,
		db: db_dependency
	):
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	user_model = db.query(Users).filter(Users.id == user.get('id'))\
		.first()
	
	if user_model is not None:
		return user_model
	raise HTTPException(status_code=404, detail='User not found.')


@router.put("/password/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_password(
		user: user_dependency,
		db: db_dependency,
		update_user_password_request: UpdateUserPasswordRequest,
		user_id: int = Path(gt=0),
	):
	if user is None or user.get('id') != user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	password = update_user_password_request.password
	new_pass = update_user_password_request.new_password
	user_model = db.query(Users).filter(Users.id == user_id)\
		.first()
		#.filter(Users.username == username)\
	if user_model is None:
		raise HTTPException(status_code=404, detail='User not found.')


	# Confirm that the token password matchs the current password in the database
	if not verify_password(password,user_model.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')
	
	# hash the new password 
	hashed_pass = hash_password(new_pass)
	# Update the user model
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
	
@router.put("/phone_number/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_phone_number(
	user: user_dependency,
	db: db_dependency,
	phone_number: str = Body(min_length=7, max_length=15),
	user_id: int = Path(gt=0),
):
	if user is None: #or user.get('id') != user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	user_model = db.query(Users).filter(Users.id == user_id)\
		.first()
	if user_model is None:
		raise HTTPException(status_code=404, detail='User not found.')
	#db.query(Users).filter(Users.id == user_id).update({"phone_number": phone_number})
	user_model.phone_number = phone_number

	try:
		db.add(user_model)
		db.commit()
		db.refresh(user_model)
		return {
			"id": user_id,
			"username": user_model.username,
			"phone_number": phone_number,
		}
	except SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Database error while updating user phone number."
		)
	
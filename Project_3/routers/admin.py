from fastapi import APIRouter,Depends, HTTPException, Path
from pydantic import BaseModel, Field
import starlette.status as status
from typing import Annotated
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Todos
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
	prefix='/admin',
	tags=['admin']
)

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


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,
				   db: db_dependency):
	if user is None or user.get('user_role') != 'admin':
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
					  db: db_dependency,
					  todo_id: int = Path(gt=0)):
	if user is None or user.get('user_role') != 'admin':
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	todo_model = db.query(Todos).filter(Todos.id == todo_id)\
		.first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail='Todo not found.')

	try:
		db.query(Todos).filter(Todos.id == todo_id)\
			.delete()
		db.commit()
	except SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Database error while deleting todo."
		)





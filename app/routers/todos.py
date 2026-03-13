from fastapi import APIRouter,Depends, HTTPException, Path
from pydantic import BaseModel, Field
import starlette.status as status
from typing import Annotated, TypeAlias
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
	prefix='/todos',
	tags=['todos']
)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

#db dependency injection
db_dependency: TypeAlias = Annotated[Session, Depends(get_db)]
# user dependency injection (token validation)
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
	title: str = Field(min_length=10)
	description: str =Field(min_length=10, max_length=1000)
	priority: int = Field(gt=0, lt=6)
	complete: bool


@router.get("/")
async def read_all(user: user_dependency,
				   db: db_dependency):
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency,
					db: db_dependency, 
					todo_id: int = Path(gt=0)):
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	todo_model = db.query(Todos).filter(Todos.id == todo_id)\
	.filter(Todos.owner_id == user.get('id')).first()
	if todo_model is not None:
		return todo_model
	raise HTTPException(status_code=404, detail='Todo not found.')

@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
					  db: db_dependency, 
					  todo_request: TodoRequest):
	try:
		if user is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
		
		#print(f'user: {user}')
		#print(f'user id: {user.get("id")}')
		todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id')) # creates an instance of this object
		db.add(todo_model) # add this object instance to the db (only in memory)
		db.commit() # commit this change to db (persist in disk/file)
		db.refresh(todo_model)  # important! so to update the instance with the generated id and any other default values set by the database
		#print(f'todo_model: {todo_model.to_dict()}')  # debug print statement to check the state of the model after refresh this way the id is generated and we can see it in the output
		return todo_model.to_dict()
	except SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating todo."
        )

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
		user: user_dependency,
		db: db_dependency, 
		todo_request: TodoRequest,
		todo_id: int = Path(gt=0) 
	):
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	todo_model = db.query(Todos).filter(Todos.id == todo_id)\
	.filter(Todos.owner_id == user.get('id')).first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail='Todo not found.')

	# updates the instance of object to update
	todo_model.title = todo_request.title
	todo_model.description = todo_request.description
	todo_model.priority = todo_request.priority
	todo_model.complete = todo_request.complete	

	try:
		db.add(todo_model) # add this object instance to the db (only in memory)
		db.commit() # commit this change to db (persist in disk/file)
		db.refresh(todo_model)  # important!
		return todo_model
	except SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating todo."
        )
	

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
	user: user_dependency,
	db: db_dependency, 
	todo_id: int = Path(gt=0) 
):
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
	todo_model = db.query(Todos).filter(Todos.id == todo_id)\
	.filter(Todos.owner_id == user.get('id')).first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail='Todo not found.')
	
	try:
		db.query(Todos).filter(Todos.id == todo_id)\
		.filter(Todos.owner_id == user.get('id')).delete()
		db.commit() # commit this change to db (persist in disk/file)
	except SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting todo."
        )
	
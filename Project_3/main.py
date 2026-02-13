from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy import inspect
from sqlalchemy.orm import Session
import models
from models import Todos
from database import SessionLocal, engine


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

@app.get("/")
async def read_all(db: Annotated[Session, Depends(get_db)]):
	return db.query(Todos).all()

# This a dummy endpoint of sorts to confirm the tables names of the db
@app.get("/tables")
async def get_tables(db: Annotated[Session, Depends(get_db)]):
	inspector = inspect(engine)
	return inspector.get_table_names()
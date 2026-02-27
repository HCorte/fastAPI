from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.routers.admin import get_db

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:7k5lwpe@localhost/testdb"

engine = create_engine(
	SQLALCHEMY_DATABASE_URL
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
	db = TestingSessionLocal()
	try: 
		yield db
	finally:
		db.close()
	
app.dependency_overrides[get_db] = override_get_db


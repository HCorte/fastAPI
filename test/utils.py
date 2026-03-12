from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from fastapi.testclient import TestClient
from app.models import Todos, Users
import pytest
from app.routers.auth import bcrypt_context

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

def override_get_current_user():
	return {'username': 'testuser', 'id': 1, 'user_role': 'admin'}


client = TestClient(app)


@pytest.fixture
def test_todo():
	# clean up DB (truncate tables) using a fresh connection if there are any leftover data from previous tests
	with engine.begin() as connection:
		connection.execute(text("TRUNCATE TABLE todos RESTART IDENTITY CASCADE;"))
		connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))

	user = Users(
		email="testuser@example.com",
		username="testuser",
		first_name="Test",
		last_name="User",
		hashed_password="hashedpassword",
		is_active=True,
		role="admin",
		phone_number="1234567890"
	)

	db = TestingSessionLocal()
	db.add(user)
	db.commit()
	db.refresh(user)

	todo = Todos(
		title="Learn to code!",
		description="Need to learn everyday!",
		priority=5,
		complete=False,
		owner_id=user.id            # <-- use real generated id
	)

	db.add(todo)
	db.commit()
	yield todo
	with engine.begin() as connection:
		connection.execute(text("TRUNCATE TABLE todos RESTART IDENTITY CASCADE;"))
		connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))

@pytest.fixture
def test_user():
	user = Users(
		username='hcorte',
		email='hcorte@lnec.pt',
		first_name='Henrique',
		last_name='Corte',
		hashed_password=bcrypt_context.hash('testpassword'),
		role='admin',
		phone_number='1234567890',
	)

	db = TestingSessionLocal()
	db.add(user)
	db.commit()
	yield user
	db.close()
	with engine.begin() as connection:
		connection.execute(text("TRUNCATE TABLE todos RESTART IDENTITY CASCADE;"))
		connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))

@pytest.fixture
def db_session():
	db = TestingSessionLocal()
	yield db
	db.close()
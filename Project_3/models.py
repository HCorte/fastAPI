from typing import Any
from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class Users(Base):
	__tablename__ = 'users'

	id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(unique=True, index=True)
	username: Mapped[str] = mapped_column(unique=True, index=True)
	first_name: Mapped[str]
	last_name: Mapped[str]
	hashed_password: Mapped[str]
	is_active: Mapped[bool] = mapped_column(default=True)
	role = Mapped[str]

	def to_dict(self) -> dict[str, Any]:
		return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class Todos(Base):
	__tablename__ = 'todos'

	#id = Column(Integer, primary_key=True, index=True)
	id: Mapped[int] = mapped_column(primary_key=True)  
	title: Mapped[str]
	description: Mapped[str]
	priority: Mapped[int]
	complete: Mapped[bool]
	ownser_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
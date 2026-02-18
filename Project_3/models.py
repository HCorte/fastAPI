from database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class Todos(Base):
	__tablename__ = 'todos'

	#id = Column(Integer, primary_key=True, index=True)
	id: Mapped[int] = mapped_column(primary_key=True)  
	title: Mapped[str]
	description: Mapped[str]
	priority: Mapped[int]
	complete: Mapped[bool]
from fastapi import FastAPI, Body
from Book import Book
from BookRequest import BookRequest

app = FastAPI()

BOOKS = [
	Book(1, 'Computer Sciend Pro', 'Python Course', 'Good book', 5),
	Book(2, 'Computer Sciend Pro 2', 'Python Course 2', 'Good book 2', 2),
	Book(3, 'Computer Sciend Pro 3', 'Python Course 3', 'Good book 3', 3),
	Book(4, 'Computer Sciend Pro 4', 'Python Course 4', 'Good book 4', 4),
	Book(5, 'Computer Sciend Pro 5', 'Python Course 5', 'Good book 5', 6),
	Book(6, 'Computer Sciend Pro 6', 'Python Course 6', 'Good book 6', 7),
]

@app.get("/books")
async def readAllBooks():
	return BOOKS

@app.post("/book")
async def createBook(book_request: BookRequest = Body()):
	new_book = Book(**book_request.model_dump())
	print(type(new_book))
	BOOKS.append(findBookById(new_book))

	# some manual validation that did for testing now using Pydantics for doing payload validation
	""" expected = set(Book.__annotations__.keys())
	received = set(book_request.keys())

	if received != expected:
		return False """
	

	
	""" for books_propertie in book.keys():
		print(books_propertie) """
	
def findBookById(book: Book):

	book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

 	# if len(BOOKS) > 0:
	# 	book.id = BOOKS[-1].id + 1
	# else:
	# 	book.id = 1

	return book

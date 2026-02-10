from fastapi import FastAPI, Body, Path, Query, HTTPException
from Book import Book
from BookRequest import BookRequest
from starlette import status

app = FastAPI()

BOOKS = [
	Book(1, 'Computer Sciend Pro', 'Python Course', 'Good book', 5),
	Book(2, 'Computer Sciend Pro 2', 'Python Course 2', 'Good book 2', 2),
	Book(3, 'Computer Sciend Pro 3', 'Python Course 3', 'Good book 3', 3),
	Book(4, 'Computer Sciend Pro 4', 'Python Course 4', 'Good book 4', 4),
	Book(5, 'Computer Sciend Pro 5', 'Python Course 5', 'Good book 5', 6),
	Book(6, 'Computer Sciend Pro 6', 'Python Course 6', 'Good book 6', 7),
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def readAllBooks():
	return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def readBook(book_id: int = Path(gt=0)):
	for book in BOOKS:
		if book.id == book_id:
			return book
	raise HTTPException(status_code=404, detail='Item not Found')
		
@app.get("/books/", status_code=status.HTTP_200_OK)
async def readBookByRating(book_rating: int = Query(gt=0, lt=6)):
	books_list = []
	for book in BOOKS:
		if book.rating == book_rating:
			books_list.append(book)
	
	return books_list

@app.post("/book", status_code=status.HTTP_201_CREATED)
async def createBook(book_request: BookRequest = Body()):
	new_book = Book(**book_request.model_dump())
	print(type(new_book))
	BOOKS.append(findBookById(new_book))
	
def findBookById(book: Book):
	book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

	return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def updateBook(book: BookRequest):
	for i in range(len(BOOKS)):
		if BOOKS[i].id == book.id:
			BOOKS[i] = Book(**book.model_dump()) # convert BookRequest -> Book
			return BOOKS[i]
	raise HTTPException(status_code=404, detail='Item not found')
	#return  {"error": "Book not found"}

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteBook(book_id: int = Path(gt=0)):
	for i in range(len(BOOKS)):
		if BOOKS[i].id == book_id:
			BOOKS.pop(i)
			return
	raise HTTPException(status_code=404, detail='Item not found')

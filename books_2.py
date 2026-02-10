from fastapi import Body, FastAPI

app = FastAPI()


BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        title = book.get('title')
        if title != None and title.casefold() == book_title.casefold():
            return book


@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        category_db= book.get('category')
        if category_db != None and category.casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/byauthor/")
async def getBookByAuthor(author: str):
    print('author: {author}')
    author_books = []
    for book in BOOKS:
        author_db = book.get('author')
        if author_db != None and author_db.casefold() == author.casefold():
            author_books.append(book)
    
    return author_books

# Get all books from a specific author using path or query parameters
""" @app.get("/books/byauthor/")
async def read_books_by_author_path(author: str):
    books_to_return = []
    for book in BOOKS:
        author_db = book.get('author')
        if author_db != None and author_db.casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return """


@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    print(f'book_author: {book_author} and category: {category}')
    books_to_return = []
    for book in BOOKS:
        author_db = book.get('author')
        category_db = book.get('category')
        print(f'author_db: {author_db}')
        if author_db != None and author_db.casefold() == book_author.casefold() and \
                category_db != None and category_db.casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return


@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)


@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        title = BOOKS[i].get('title')
        if title != None and title.casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        title = BOOKS[i].get('title')
        if title != None and title.casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

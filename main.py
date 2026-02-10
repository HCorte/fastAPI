from fastapi import FastAPI

app = FastAPI()

@app.get("/api-endpoint")
async def first_api():
	return {"message": "Hello Henrique!"}


books = [
	{"title": "Title One", "author": "Author One", "category": "science"},
	{"title": "Title Two", "author": "Author Two", "category": "science"},
	{"title": "Title Three", "author": "Author Three", "category": "history"},
	{"title": "Title Four", "author": "Author Four", "category": "math"},
	{"title": "Title Five", "author": "Author Five", "category": "math"},
]
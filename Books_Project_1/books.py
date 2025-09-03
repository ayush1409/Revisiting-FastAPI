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
async def all_books():
    return BOOKS

@app.get("/books/{title}")
async def get_book_by_title(title: str):
    books = []
    for book in BOOKS:
        if book.get('title').casefold() == title.casefold():
            books.append(book)
    return books

@app.get("/books/")
async def get_books_by_query(category: str):
    books = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books.append(book)
    return books

@app.get("/books/author/{book_author}/")
async def get_books_by_author(book_author: str, category: str):
    books = []
    print(f"book_author: {book_author}, category: {category}")
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
            book.get('category').casefold() == category.casefold():
            books.append(book)
    return books

@app.post("/books")
async def create_book(book=Body()):
    print(book)
    BOOKS.append(book)
    return {"message": "Book added"}

@app.put("/books")
async def update_book(book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book.get('title').casefold():
            BOOKS[i] = book
    
@app.delete("/books/{title}")
async def delete_book(title: str):
    removed_book = []
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == title.casefold():
            removed_book = BOOKS.pop(i)
    return {"Removed Book": removed_book}
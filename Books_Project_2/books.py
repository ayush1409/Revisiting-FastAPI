from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID not needed when creating book", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1950, lt=2025)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Programming in Python",
                "author": "Harry",
                "description": "Python everyday",
                "rating": 5,
                "published_date": 2012
            }
        }
    }

BOOKS = [
    Book(1, "Computer Science", "Turing", "CS Fundamentals", 5, 2020),
    Book(2, "History", "Peter", "History Fundamentals", 3, 1971),
    Book(3, "Chemistry", "Tony", "Chemistry Fundamentals", 4, 2009),
    Book(4, "Physics", "HC Verma", "Physics Fundamentals", 5, 1996),
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def get_all_books():
    return {"data": BOOKS}

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")

def update_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    new_book = Book(**book.model_dump())
    BOOKS.append(update_book_id(new_book))

# Get book by rating(query parameter)
@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_book_by_rating(rating: int = Query(gt=0, lt=6)):
    books = []
    for book in BOOKS:
        if book.rating == rating:
            books.append(book)
    return books

# Update a book using PUT
@app.put("/books", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(request_book: BookRequest):
    book_updated = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == request_book.id:
            BOOKS[i] = Book(**request_book.model_dump())
            book_updated = True
            break
    if not book_updated:
        raise HTTPException(status_code=404, detail="Item not found")

# Get book by publish date
@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def get_book_by_date(publish_date: int = Query(lt=1950, gt=2025)):
    data = []
    for book in BOOKS:
        if book.published_date == publish_date:
            data.append(book)
    return {"data": data}

# Delete book
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    data = None
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            data = BOOKS.pop(i)
            return {"removed": data}
    raise HTTPException(status_code=404, detail="Item not found")


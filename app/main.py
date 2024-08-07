from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    year = Column(Integer)
    description = Column(String)
    image_url = Column(String)

engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def optimize_image(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        # Optimize image here, e.g., resizing, compression, etc.
        return image_url
    except UnidentifiedImageError as e:
        print(f"Error: Cannot identify image file at {image_url}. {e}")
        return None

@app.on_event("startup")
async def load_books():
    with open('load_books.json', encoding='utf-8') as f:
        books_data = json.load(f)

    session = SessionLocal()
    for book_data in books_data:
        book_id = book_data['id']
        optimized_image_url = optimize_image(book_data['фотография'])

        existing_book = session.execute(select(Book).where(Book.id == book_id)).first()
        if not existing_book:
            book = Book(
                id=book_id,
                title=book_data['название'],
                author=book_data['автор'],
                year=book_data['год публикации'],
                description=book_data['описание'],
                image_url=optimized_image_url
            )
            session.add(book)
    session.commit()

@app.get("/")
def home_page():
    return {
        "message": "Приветствую вас в данном Fast API приложении",
        "message_1": "Полезные страницы:",
        "message_2": "http://127.0.0.1:8001/books",
        "message_3": "http://127.0.0.1:8001/docs",
        "message_4": "http://127.0.0.1:8001/book/{id}"
    }

@app.get("/books")
async def read_books():
    session = SessionLocal()
    books = session.query(Book).all()
    return [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "description": book.description,
            "image_url": book.image_url
        }
        for book in books
    ]

@app.get("/books/{id}")
async def get_book_by_id(
    id: int,
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    year: Optional[int] = Query(None)
):
    session = SessionLocal()
    book = session.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    filtered_books = [book]

    if title is not None:
        filtered_books = [book for book in filtered_books if book.title.lower() == title.lower()]

    if author is not None:
        filtered_books = [book for book in filtered_books if book.author.lower() == author.lower()]

    if year is not None:
        filtered_books = [book for book in filtered_books if book.year == year]

    return [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "description": book.description,
            "image_url": book.image_url
        }
        for book in filtered_books
    ]

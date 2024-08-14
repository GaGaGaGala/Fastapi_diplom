from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json

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

@app.on_event("startup")
async def load_books():
    with open('load_books.json', encoding='utf-8') as f:
        books_data = json.load(f)

    session = SessionLocal()
    for book_data in books_data:
        book_id = book_data['id']


        existing_book = session.execute(select(Book).where(Book.id == book_id)).first()
        if not existing_book:
            book = Book(
                id=book_id,
                title=book_data['название'],
                author=book_data['автор'],
                year=book_data['год публикации'],
                description=book_data['описание'],
                image_url=book_data["фотография"]
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
async def get_book_by_id(id: int):
    session = SessionLocal()
    book = session.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "description": book.description,
        "image_url": book.image_url
    }

@app.get("/search_book/")
async def get_searched_book(title: str | None = None,
                            author: str | None = None,
                            year: int | None = None):
    print(locals())
    session = SessionLocal()
    filtered_books = session.query(Book).all()
    if title is not None:
        filtered_books = [book for book in filtered_books if title.lower() in book.title.lower()]

    if author is not None:
        filtered_books = [book for book in filtered_books if author.lower() in book.title.lower()]

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

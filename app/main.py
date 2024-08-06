from fastapi import FastAPI
from sqlalchemy import select, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from typing import List, Optional

from utils import json_to_dict_list

app = FastAPI()

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
        # Оптимизация изображения здесь, например, изменение размера, компрессия и т.д.
        return image_url
    except UnidentifiedImageError as e:
        print(f"Error: Cannot identify image file at {image_url}. {e}")
        return None


from sqlalchemy import select

@app.on_event("startup")
async def load_books():
    with open('load_books.json', encoding='utf-8') as f:
        books_data = json.load(f)

    session = SessionLocal()
    for book_data in books_data:
        book_id = book_data['id']
        optimized_image_url = optimize_image(book_data['фотография'])

        # Проверяем, существует ли уже книга с таким id
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
    return {"message": "Приветствую вас в данном Fast API приложении",
            "message_1": "Полезные страницы:",
            "message_2": "http://127.0.0.1:8001/books",
            "message_3": "http://127.0.0.1:8001/docs",
            "message_4": "http://127.0.0.1:8001/book/{id}"
            }

@app.get("/books")
async def read_books():
    session = SessionLocal()
    books = session.query(Book).all()
    return [{"id": book.id,
             "title": book.title,
             "author": book.author,
             "year": book.year,
             "description": book.description,
             "image_url": book.image_url} for book in books]

@app.get("/books/{id}")
def get_all_books_id(id: Optional[int] = None,
                     title: Optional[str] = None,
                     author: Optional[str] = None,
                     year: Optional[int] = None):
    books = json_to_dict_list(json.load())
    filtered_books = []
    for book in books:
        if book["id"] == id:
            filtered_books.append(book)

    if title:
        filtered_books = [book for book in filtered_books if book['title'].lower() == title.lower()]

    if year:
        filtered_books = [book for book in filtered_books if book['year'] == year]

    return filtered_books
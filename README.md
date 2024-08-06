python -m pip install -r requirements.txt

[Flask] python app.py
[FastAPI] python -m uvicorn app.main:app
[Django] python manage.py runserver

```
├── app
│   └── # user
│   ├── # routes.py
│   └── main.py
├── tests/
│   ├── # users
│   └── test.py
├── load_books.json
├── utils.py
├── pyproject.toml или requirements.txt
├── .env
└── .gitignore
```
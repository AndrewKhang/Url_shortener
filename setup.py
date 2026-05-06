import os

structure = [
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/database.py",
    "app/models/link.py",
    "app/schemas/link.py",
    "app/routes/link.py",
    "app/services/shortener.py"
]

for path in structure:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "a").close()
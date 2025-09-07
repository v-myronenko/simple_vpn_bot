# run_once.py
# 1) ІМПОРТУЄМО МОДЕЛІ, щоб вони зареєструвались у Base.metadata
import db.models  # noqa: F401

# 2) Лише потім тягнемо Base та engine і створюємо таблиці
from db.base import engine, Base

Base.metadata.create_all(bind=engine)

print("DB created ✓")

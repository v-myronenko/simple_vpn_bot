from datetime import datetime

from sqlalchemy.orm import Session

from app.models import User


class UserService:
    """Сервіс для роботи з користувачами."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, telegram_id: int, language: str | None = None) -> User:
        """
        Повертає існуючого користувача або створює нового.
        Якщо передана language і вона відрізняється від поточної — оновлює її.
        """
        user = (
            self.db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if user:
            if language and language != user.language:
                user.language = language
                self.db.commit()
                self.db.refresh(user)
            return user

        # створюємо нового юзера
        user = User(
            telegram_id=telegram_id,
            language=language,
            created_at=datetime.utcnow(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

from pydantic import BaseModel


class TelegramStarsCompleteRequest(BaseModel):
    """Запит від бота до бекенду після успішної оплати Stars."""
    telegram_id: int


class TelegramStarsCompleteResponse(BaseModel):
    """Проста відповідь-заглушка для MVP."""
    ok: bool
    message: str

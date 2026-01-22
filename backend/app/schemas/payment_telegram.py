from pydantic import BaseModel


class TelegramStarsCompleteRequest(BaseModel):
    telegram_id: int

from fastapi import APIRouter, HTTPException
from app.schemas import TelegramStarsCompleteRequest, TelegramStarsCompleteResponse

router = APIRouter(
    prefix="/api/payment/telegram",
    tags=["payments"],
)


@router.post("/stars-complete", response_model=TelegramStarsCompleteResponse)
async def telegram_stars_complete(payload: TelegramStarsCompleteRequest):
    """
    Webhook, который будет вызываться Telegram Stars после успешной оплаты.
    Пока просто возвращаем заглушку.
    """
    # TODO: здесь потом:
    #  1) провалидируем подпись (если будет)
    #  2) найдём/создадим пользователя по telegram_id
    #  3) создадим подписку, начислим дни
    #  4) запишем платёж в таблицу payments
    if not payload.telegram_id:
        raise HTTPException(status_code=400, detail="telegram_id is required")

    return TelegramStarsCompleteResponse(
        ok=True,
        message="Payment received (stub). Subscription will be activated soon.",
    )

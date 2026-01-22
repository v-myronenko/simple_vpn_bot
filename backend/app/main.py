from fastapi import FastAPI

from app.core.config import settings
from app.routers import health, user_subscription, payment_telegram


app = FastAPI(title=settings.APP_NAME)

# системний healthcheck
app.include_router(health.router)

# робота з користувачами / підписками
app.include_router(user_subscription.router)

# 💰 оплати через Telegram Stars (наш новий роутер)
app.include_router(payment_telegram.router)

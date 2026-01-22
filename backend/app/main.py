from fastapi import FastAPI

from app.core.config import settings
from app.routers import health, user_subscription

app = FastAPI(title=settings.APP_NAME)

app.include_router(health.router)
app.include_router(user_subscription.router)

from fastapi import FastAPI

from app.routers import health, user_subscription, payment_telegram

app = FastAPI(
    title="svpn-backend",
    version="0.1.0",
)


# Routers
app.include_router(health.router)
app.include_router(user_subscription.router)
app.include_router(payment_telegram.router)


@app.get("/")
async def root():
    return {"status": "ok"}

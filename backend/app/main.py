from fastapi import FastAPI

from app.routers import health, user_subscription, payment_telegram, vpn_config

app = FastAPI(
    title="svpn-backend",
    version="0.1.0",
)


# Routers
app.include_router(health.router)
app.include_router(user_subscription.router)
app.include_router(payment_telegram.router, prefix="/api")
app.include_router(vpn_config.router)  # у нього вже prefix="/api/users"


@app.get("/")
async def root():
    return {"status": "ok"}

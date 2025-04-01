from aiohttp import web
from datetime import datetime, timedelta
import config
import database
from main import bot


async def handle_cryptobot_webhook(request):
    try:
        data = await request.json()
        print("[Webhook] Data received:", data)

        # Перевірка чи оплата пройшла
        if data.get("status") == "paid":
            payload = data.get("payload")  # Має бути Telegram ID
            if not payload:
                return web.Response(text="No payload", status=400)

            user_id = int(payload)
            user = database.get_user_by_telegram_id(user_id)
            if not user:
                return web.Response(text="User not found", status=404)

            # Продовжуємо доступ
            new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
            database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))

            try:
                await bot.send_message(
                    user_id,
                    f"✅ Ваш доступ продовжено до {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Дякуємо за оплату!"
                )
            except Exception as e:
                print("[Telegram Error]", e)

        return web.Response(text="OK")

    except Exception as e:
        print("[Webhook Error]", e)
        return web.Response(text="Internal Server Error", status=500)


# -------- Запуск сервера --------
app = web.Application()
app.add_routes([web.post("/cryptobot/webhook", handle_cryptobot_webhook)])

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)  # або 443, якщо ти з https

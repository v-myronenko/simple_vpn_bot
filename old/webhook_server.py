# webhook_server.py
import traceback

from aiohttp import web
from datetime import datetime, timedelta
import config
import database
from main import bot

async def handle_cryptobot_webhook(request):
    try:
        data = await request.json()
        print("[Webhook] Received data:", data)

        if data.get("update_type") != "invoice_paid":
            print("[Webhook] Unpaid invoice or other type of event")
            return web.Response(text="Ignored", status=200)

        payload = data.get("payload", {})
        user_id_str = payload.get("payload")
        print("[Webhook] Payload із user_id:", user_id_str)

        if not user_id_str:
            print("[Webhook] There is no user_id in payload")
            return web.Response(text="No user ID", status=200)

        user_id = int(user_id_str)
        user = database.get_user_by_telegram_id(user_id)
        print("[Webhook] User from db:", user)

        if not user:
            print("[Webhook] User not found")
            return web.Response(text="User not found", status=200)

        new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
        print("[Webhook] New access period:", new_end)

        database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))

        try:
            await bot.send_message(user_id,
                f"✅ Your access extended to {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Thank you for payment!")
            print("[Webhook] Message sent to user")
        except Exception as e:
            print("[Webhook] Error sending message:", e)

        # 🔥 ОБОВ'ЯЗКОВО ПОВЕРТАЄМО 200 OK НАВІТЬ ЯКЩО ПОМИЛКА ВНУТРІ
        return web.Response(text="OK", status=200)

    except Exception as e:
        print("[Webhook] Error:", e)
        traceback.print_exc()
        return web.Response(text="Server error", status=500)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/webhook", handle_cryptobot_webhook)
    web.run_app(app, port=8000)





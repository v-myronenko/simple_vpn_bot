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

        if data.get("update_type") == "invoice_paid":
            payload_data = data.get("payload", {})
            user_id = int(payload_data.get("payload"))  # <- витягуємо внутрішній payload

            if not user_id:
                return web.Response(text="No user_id", status=400)

            # далі стандартна логіка:
            user = database.get_user_by_telegram_id(user_id)
            if not user:
                return web.Response(text="User not found", status=404)

            new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
            database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))

            try:
                await bot.send_message(
                    user_id,
                    f"✅ Your VPN access extendet to {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Thank you!"
                )
            except Exception as e:
                print(f"[Webhook] Помилка надсилання повідомлення: {e}")

            return web.Response(text="OK", status=200)

    except Exception as e:
        print("[Webhook] Помилка:", e)
        traceback.print_exc()  # покаже повний стек трейс
        return web.Response(text="Server error", status=500)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/webhook", handle_cryptobot_webhook)
    web.run_app(app, port=8443)



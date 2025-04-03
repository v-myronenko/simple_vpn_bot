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
            print("[Webhook] Неоплачений інвойс або інший тип події")
            return web.Response(status=200)

        payload = data.get("payload", {})
        user_id_str = payload.get("payload")
        print("[Webhook] Payload із user_id:", user_id_str)

        if not user_id_str:
            print("[Webhook] Немає user_id у payload")
            return web.Response(status=200)

        user_id = int(user_id_str)
        user = database.get_user_by_telegram_id(user_id)
        print("[Webhook] Користувач з бази:", user)

        if not user:
            print("[Webhook] Користувач не знайдений")
            return web.Response(status=200)

        new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
        print("[Webhook] Новий термін доступу до:", new_end)

        database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))

        try:
            await bot.send_message(user_id,
                                   f"✅ Ваш доступ продовжено до {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Дякуємо за оплату!")
            print("[Webhook] Повідомлення користувачу надіслано")
        except Exception as e:
            print("[Webhook] Помилка надсилання повідомлення:", e)

            return web.Response(text="OK", status=200)

    except Exception as e:
        print("[Webhook] Помилка:", e)
        traceback.print_exc()  # покаже повний стек трейс
        return web.Response(text="Server error", status=500)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/webhook", handle_cryptobot_webhook)
    web.run_app(app, port=8444)




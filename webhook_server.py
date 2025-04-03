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
        print("[Webhook] Отримано дані:", data)

        # Перевіряємо тип події
        if data.get("update_type") != "invoice_paid":
            return web.Response(text="Not an invoice_paid update", status=200)

        # Беремо payload
        invoice = data.get("payload")
        if not invoice:
            return web.Response(text="No payload", status=400)

        # Отримуємо user_id з payload
        user_id = invoice.get("payload")  # Це має бути telegram ID
        if not user_id:
            return web.Response(text="No user ID", status=400)

        # Продовжуємо доступ
        new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
        database.extend_subscription(int(user_id), new_end.strftime("%Y-%m-%d %H:%M:%S"))

        # Відправляємо повідомлення
        try:
            await bot.send_message(user_id,
                                   f"✅ Ваш доступ продовжено до {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Дякуємо за оплату!")
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



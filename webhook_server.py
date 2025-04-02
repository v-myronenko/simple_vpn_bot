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

        # Перевіряємо, чи це подія успішної оплати
        if data.get("update_type") != "invoice_paid":
            return web.Response(text="Not invoice_paid", status=200)

        payload_data = data.get("payload", {})
        user_id_str = payload_data.get("payload")

        if not user_id_str:
            return web.Response(text="No payload inside", status=400)

        try:
            user_id = int(user_id_str)
        except ValueError:
            return web.Response(text="Invalid payload format", status=400)

        # Знаходимо користувача
        user = database.get_user_by_telegram_id(user_id)
        if not user:
            return web.Response(text="User not found", status=404)

        # Продовжуємо підписку
        new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
        database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))

        # Повідомляємо користувача
        try:
            await bot.send_message(user_id, f"✅ Ваш доступ продовжено до {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Дякуємо за оплату!")
        except Exception as e:
            print(f"[Webhook] Помилка надсилання повідомлення: {e}")

        return web.Response(text="OK", status=200)


    except Exception as e:
        print("[Webhook] Помилка:", e)
        traceback.print_exc()  # покаже повний стек трейс
        return web.Response(text="Server error", status=500)

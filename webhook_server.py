from datetime import datetime, timedelta

from aiohttp import web

import config
import database
from main import bot


async def handle_cryptobot_webhook(request):
    try:
        data = await request.json()
        print("[Webhook] Data received:", data)

        # Перевірка, чи є статус 'paid' в даних
        if data.get("status") == "paid":
            payload = data.get("payload")  # Отримуємо payload з даних
            if not payload:
                return web.Response(text="No payload", status=400)

            # Перетворюємо отриманий payload (який є рядком) на ціле число
            user_id = int(payload)  # Тепер payload є рядком, і ми безпосередньо перетворюємо його

            user = database.get_user_by_telegram_id(user_id)
            if not user:
                return web.Response(text="User not found", status=404)

            # Подовжуємо термін дії підписки
            new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
            database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))

            # Надсилаємо повідомлення користувачу
            try:
                await bot.send_message(user_id, f"✅ Ваш доступ продовжено до {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Дякуємо за оплату!")
            except Exception as e:
                print("Помилка надсилання повідомлення:", e)

        return web.Response(text="OK")

    except Exception as e:
        print("Webhook error:", e)
        return web.Response(text="Error", status=500)



app = web.Application()
app.router.add_post("/webhook", handle_cryptobot_webhook)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)


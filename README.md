# simple_vpn_bot (спрощене MVP)

Мінімальний телеграм-бот для керування підпискою: `/start` (створює юзера, дає тріал на 7 днів, якщо ще нічого не було) і `/myvpn` (показує статус).

## Вимоги

- Python 3.12+
- SQLite (встанови `sqlite3` для скриптів)
- Токен бота в `TELEGRAM_TOKEN`

## Локальний запуск

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# створити .env на основі .env.example
export TELEGRAM_TOKEN=...            # або додай у свій .env і експортуй
export DATABASE_URL=sqlite:////ABS/PATH/simple_vpn_bot_local.db

python bot.py

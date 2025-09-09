# simple_vpn_bot — SQLite scaffold

Це мінімальний каркас із SQLite + SQLAlchemy, готовий до розширення (Stars/USDT/x-ui).

## Швидкий старт 

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env  # заповни токени
python run_once.py     # створює БД
python bot.py          # запуск бота
```

## Структура
- `bot.py` — точка входу (команди /start, /my_account, кнопка купівлі)
- `config.py` — налаштування (ENV)
- `db/` — SQLAlchemy: engine, моделі, CRUD
- `handlers/` — хендлери телеграму
- `services/` — інтеграції (x-ui, billing)
- `utils/` — планувальник перевірки підписок, логування

## Гілки/PR-план
1. `feature/sqlite` — цей каркас
2. `feature/stars` — реальна інтеграція Stars
3. `feature/xui` — UUID add/remove при активації/експірації
4. `feature/usdt` — ручні платежі з підтвердженням адміністратором

## Команди для Git
```bash
git checkout -b feature/sqlite
# додай файли
git add .
git commit -m "feat(db): SQLite scaffold, handlers, CRUD, scheduler"
git push origin feature/sqlite
# створи PR у GitHub
```

from app.db.session import SessionLocal
from app.models import Plan, Server


def run_initial_seed() -> None:
    db = SessionLocal()
    try:
        # ---- SEED PLANS ----
        basic_plan_code = "basic_30d"

        basic_plan = (
            db.query(Plan)
            .filter(Plan.code == basic_plan_code)
            .first()
        )

        if not basic_plan:
            basic_plan = Plan(
                code=basic_plan_code,
                name="Basic 30 days",
                duration_days=30,
                price_stars=1000,  # TODO: потім оновимо під реальний прайс
                is_active=True,
            )
            db.add(basic_plan)
            print(f"[SEED] Created plan: {basic_plan.code}")
        else:
            print(f"[SEED] Plan already exists: {basic_plan.code}")

        # ---- SEED SERVERS ----
        server_name = "frankfurt-1"

        server = (
            db.query(Server)
            .filter(Server.name == server_name)
            .first()
        )

        if not server:
            server = Server(
                name=server_name,
                region="EU",
                provider_type="xray_vless_reality",
                api_url=None,       # TODO: заповнимо при підключенні реального сервера
                api_user=None,
                api_password=None,
                api_token=None,
                is_active=True,
            )
            db.add(server)
            print(f"[SEED] Created server: {server.name}")
        else:
            print(f"[SEED] Server already exists: {server.name}")

        db.commit()
        print("[SEED] Done.")

    finally:
        db.close()


if __name__ == "__main__":
    run_initial_seed()

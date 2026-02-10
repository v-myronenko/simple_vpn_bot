from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.services.deactivation_service import DeactivationService


def main():
    setup_logging()  # JSON-логи в stdout

    db = SessionLocal()
    try:
        service = DeactivationService(db)
        service.deactivate_expired_trials()
        service.deactivate_expired_subscriptions()
    finally:
        db.close()


if __name__ == "__main__":
    main()

from app.db.session import SessionLocal
from app.services.deactivation_service import DeactivationService


def main():
    db = SessionLocal()
    try:
        service = DeactivationService(db)
        service.deactivate_expired_trials()
        service.deactivate_expired_subscriptions()
    finally:
        db.close()


if __name__ == "__main__":
    main()

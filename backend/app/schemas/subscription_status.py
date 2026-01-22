from datetime import datetime

from pydantic import BaseModel


class SubscriptionInfo(BaseModel):
    plan_code: str
    plan_name: str
    end_at: datetime
    server_name: str
    server_region: str


class SubscriptionStatusResponse(BaseModel):
    user_exists: bool
    has_active_subscription: bool
    subscription: SubscriptionInfo | None

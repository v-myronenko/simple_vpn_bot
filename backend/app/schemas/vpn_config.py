from datetime import datetime

from pydantic import BaseModel


class VpnConfigResponse(BaseModel):
    ok: bool
    message: str

    # Мінімум, що треба боту:
    uuid: str | None = None
    server_name: str | None = None
    server_region: str | None = None

    # Інфо про тріал
    is_trial: bool = False
    trial_end_at: datetime | None = None

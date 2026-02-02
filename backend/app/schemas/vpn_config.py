from datetime import datetime

from pydantic import BaseModel


class VpnConfigResponse(BaseModel):
    ok: bool
    message: str

    vless_url: str
    uuid: str
    server_name: str | None = None
    server_region: str | None = None

    is_trial: bool = False
    trial_end_at: datetime | None = None

    qr_png_base64: str | None = None

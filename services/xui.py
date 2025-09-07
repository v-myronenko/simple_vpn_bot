import httpx
from config import settings

class XUI:
    def __init__(self):
        self.base = (settings.XUI_URL or "").rstrip("/")
        self.client = httpx.Client(base_url=self.base, timeout=20)
        self.token = None

    def login(self):
        # TODO: реалізувати логін у x-ui
        pass

    def add_uuid(self, inbound_id: int, user_uuid: str, remark: str):
        # TODO: POST до x-ui API
        pass

    def remove_uuid(self, inbound_id: int, user_uuid: str):
        # TODO
        pass

from venv import logger

import requests
import config
import json

BASE_URL = f"http://{config.VPN_SERVER_IP}:{config.XUI_API_PORT}"
SESSION = requests.Session()
SESSION.headers.update({"Content-Type": "application/json"})

# Замість токена використовуємо cookie "session"
SESSION.cookies.set("session", config.XUI_SESSION_COOKIE)

def get_inbound_settings():
    try:
        response = SESSION.post(
            f"{BASE_URL}/xui/inbound/list",
            headers={"Content-Type": "application/json"},
            cookies={"session": config.XUI_SESSION_COOKIE}
        )
        response.raise_for_status()
        data = response.json()
        logger.debug(f"[XUI][DEBUG get_inbound_settings] response.json = {data}")
        return data.get("obj")  # повертає список inbound
    except Exception as e:
        logger.error(f"[XUI][ERROR get_inbound_settings] {e}")
        return None

def add_user_to_xui(uuid: str, inbound_id: int) -> bool:
    inbounds = get_inbound_settings()
    if not inbounds:
        logger.warning("[XUI] Не вдалося отримати налаштування inbound")
        return False

    inbound = next((i for i in inbounds if i["id"] == config.INBOUND_ID), None)
    if not inbound:
        logger.warning("[XUI] Не знайдено inbound з вказаним ID")
        return False

    try:
        # Конвертуємо JSON-рядки в словники для редагування
        inbound_settings = json.loads(inbound["settings"])
        inbound_stream = json.loads(inbound.get("streamSettings", "{}"))
        inbound_sniffing = json.loads(inbound.get("sniffing", "{}"))

        # Додаємо UUID у список клієнтів
        inbound_settings["clients"].append({
            "id": uuid,
            "alterId": 0
        })

        payload = {
            "id": inbound_id,
            "up": inbound.get("up", 0),
            "down": inbound.get("down", 0),
            "total": inbound.get("total", 0),
            "remark": inbound.get("remark", ""),
            "enable": True,
            "expiryTime": 0,
            "listen": inbound.get("listen", None),
            "port": inbound.get("port"),
            "protocol": inbound.get("protocol"),
            "settings": json.dumps(inbound_settings),
            "streamSettings": json.dumps(inbound_stream),
            "sniffing": json.dumps(inbound_sniffing)
        }

        logger.debug(f"[XUI][DEBUG add_user_to_xui] Sending payload: {payload}")

        url = f"{BASE_URL}/xui/inbound/update/{inbound_id}"
        response = SESSION.post(url, json=payload)
        response.raise_for_status()

        logger.info(f"[XUI] Користувача {uuid} додано до inbound {inbound_id}")
        return True
    except Exception as e:
        logger.error("[XUI][ERROR add_user_to_xui] %s", e)
        return False

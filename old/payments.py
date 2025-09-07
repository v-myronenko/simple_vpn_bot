import requests
import logging
import config

API_URL = "https://pay.crypt.bot/api/"
HEADERS = {"Crypto-Pay-API-Token": config.CRYPTOBOT_TOKEN}

def create_invoice(asset, amount, payload):
    params = {
        "asset": asset,
        "amount": amount,
        "payload": str(payload),
        "description": "Donation for SVPN subscription",
        "hidden_message": "Thank you! Your access will be extended",
        "paid_btn_name": "viewItem",
        "paid_btn_url": "https://t.me/svpnFunBot"
    }
    try:
        response = requests.post(f"{API_URL}createInvoice", json=params, headers=HEADERS)
        response.raise_for_status()
        result = response.json()
        if result.get("ok"):
            invoice = result["result"]
            return invoice["invoice_id"], invoice["pay_url"]
        else:
            logging.error(f"[ERROR create_invoice] {result}")
            return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR create_invoice] {e}")
        return None, None

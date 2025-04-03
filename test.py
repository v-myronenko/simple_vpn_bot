import json

raw = '''{"update_id":37694754,"update_type":"invoice_paid","request_date":"2025-04-02T17:03:15.978Z","payload":{"invoice_id": 23355449,"hash": "IVECrmWQmMWh","currency_type": "crypto","asset": "USDT","amount": "2.6","paid_asset": "USDT", "paid_amount": "2.6","fee_asset": "USDT","fee_amount": "0.078","fee": "0.078","fee_in_usd":"0.07800192","pay_url": "https://t.me/CryptoBot?start=IVECrmWQmMWh", "bot_invoice_url": "https://t.me/CryptoBot?start=IVECrmWQmMWh", "mini_app_invoice_url": "https://t.me/CryptoBot/app?startapp=invoice-IVECrmWQmMWh&mode=compact", "web_app_invoice_url": "https://app.send.tg/invoices/IVECrmWQmMWh", "description": "Donation for SVPN subscription", "status": "paid", "created_at": "2025-04-02T16:59:04.659Z", "allow_comments": true, "allow_anonymous": true, "paid_usd_rate": "1.00002469", "usd_rate": "1.00002469", "paid_at": "2025-04-02T17:03:05.198Z", "paid_anonymously": false, "hidden_message": "Thank you! Your access will be extended", "payload": "6570494694", "paid_btn_name": "viewItem", "paid_btn_url": "https://t.me/svpnFunBot"}}'''

data = json.loads(raw)
print(data)

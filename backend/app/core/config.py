from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "svpn-backend"
    ENV: str = "dev"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: str = "change_me"

    DATABASE_URL: str = "sqlite:///./svpn.db"
    TZ: str = "Europe/Warsaw"

    # --- 3x-ui / VPN ---
    THREEXUI_USERNAME: str = "admin"
    THREEXUI_PASSWORD: str = "change_me"
    THREEXUI_INBOUND_ID: int = 1

    # --- VLESS REALITY client config (для побудови URI) ---
    VPN_REALITY_HOST: str = "116.203.58.146"  # або домен, якщо є
    VPN_REALITY_PORT: int = 443

    # pbk з конфігурації Xray (Reality)
    VPN_REALITY_PUBLIC_KEY: str = "TRkj28W1soPA3Vp9y_crsdEIq2-zawUok3cx8XOwAmo"

    # те, що ти вже використовуєш у inbound
    VPN_REALITY_SNI: str = "www.microsoft.com"
    VPN_REALITY_FINGERPRINT: str = "chrome"
    VPN_REALITY_FLOW: str = "xtls-rprx-vision"

    # якщо у твоєму inbound є shortId — додай його сюди, інакше залиш пустим
    VPN_REALITY_SHORT_ID: str | None = None

settings = Settings()

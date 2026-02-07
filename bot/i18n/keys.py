from enum import StrEnum


class I18nKey(StrEnum):
    # /start + онбординг
    START_WELCOME = "start.welcome"
    START_TRIAL_INFO = "start.trial_info"
    START_ACTIVE_SUB = "start.active_sub"
    START_NO_SUB = "start.no_sub"

    # Кнопки основного меню
    BTN_GET_VPN = "btn.get_vpn"
    BTN_BUY = "btn.buy"
    BTN_PROFILE = "btn.profile"
    BTN_SHOW_ACCESS_ACTIVE = "btn.show_access_active"
    BTN_RENEW = "btn.renew"
    BTN_TRIAL = "btn.trial"
    BTN_HELP = "btn.help"

    # Кнопка мови + тексти
    BTN_LANGUAGE = "btn.language"
    LANG_SELECT_PROMPT = "language.select_prompt"
    LANG_UPDATED = "language.updated"

    # Помилки / системні
    ERR_GENERIC = "error.generic"
    ERR_BACKEND = "error.backend"

    # Підписки
    SUB_EXPIRED = "subscription.expired"

    # Платежі / інвойс
    INVOICE_TITLE = "payment.invoice_title"
    INVOICE_DESCRIPTION = "payment.invoice_description"
    PAYMENT_ACTIVATING = "payment.activating"
    PAYMENT_BACKEND_FAIL = "payment.backend_fail"
    PAYMENT_SUCCESS_WITH_END = "payment.success_with_end"
    PAYMENT_SUCCESS_GENERIC = "payment.success_generic"

    # VPN-конфіг
    TRIAL_EXPIRED = "vpn.trial_expired"
    VPN_FETCH_ERROR = "vpn.fetch_error"
    VPN_SETTINGS_TITLE = "vpn.settings_title"
    VPN_TRIAL_INFO = "vpn.trial_info"

    # Допомога
    HELP_TEXT = "help.text"

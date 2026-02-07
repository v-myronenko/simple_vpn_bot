from .keys import I18nKey

TRANSLATIONS = {
    I18nKey.START_WELCOME: "Welcome to SVPN 👋",
    I18nKey.START_TRIAL_INFO: "You get a 3-day trial after first use.",
    I18nKey.BTN_LANGUAGE: "Language",
    I18nKey.LANG_SELECT_PROMPT: "Choose the interface language for SVPN:",
    I18nKey.LANG_UPDATED: "Language updated. If something didn't refresh, press /start.",

    I18nKey.START_ACTIVE_SUB: (
        "✅ You have an active subscription.\n\n"
        "Plan: <b>{plan_name}</b>\n"
        "Until: <b>{end_at}</b>\n"
        "Server: <b>{server_name} ({server_region})</b>\n\n"
        "Press the button below to get or refresh your connection settings."
    ),
    I18nKey.START_NO_SUB: (
        "You don't have an active SVPN subscription yet.\n\n"
        "Press the button below to choose a plan and subscribe."
    ),

    I18nKey.BTN_GET_VPN: "Get VPN",
    I18nKey.BTN_BUY: "Buy subscription",
    I18nKey.BTN_PROFILE: "My profile",
    I18nKey.BTN_SHOW_ACCESS_ACTIVE: "My VPN access",
    I18nKey.BTN_RENEW: "Renew subscription",
    I18nKey.BTN_TRIAL: "Get trial access",
    I18nKey.BTN_HELP: "Help",

    I18nKey.SUB_EXPIRED: "Your subscription has expired.",
    I18nKey.ERR_GENERIC: "Something went wrong. Please try again.",
    I18nKey.ERR_BACKEND: "Error while contacting the server. Please try again later.",

    I18nKey.INVOICE_TITLE: "SVPN — 30 days subscription",
    I18nKey.INVOICE_DESCRIPTION: (
        "Access to SVPN for 30 days. After payment your subscription will be activated automatically."
    ),
    I18nKey.PAYMENT_ACTIVATING: "✅ Payment received! Activating your subscription...",
    I18nKey.PAYMENT_BACKEND_FAIL: (
        "⚠️ Payment went through, but we couldn't confirm your subscription.\n"
        "Please contact support — we will fix it quickly."
    ),
    I18nKey.PAYMENT_SUCCESS_WITH_END: (
        "🎉 Subscription is active!\n\n"
        "Valid until: <b>{end_at}</b>"
    ),
    I18nKey.PAYMENT_SUCCESS_GENERIC: (
        "🎉 Subscription activated! (Details will be updated in /start)"
    ),

    I18nKey.TRIAL_EXPIRED: (
        "Your trial access is no longer available.\n\n"
        "To continue using SVPN, please purchase a subscription from the menu."
    ),
    I18nKey.VPN_FETCH_ERROR: (
        "Failed to fetch VPN configuration. "
        "Please try again later or contact support."
    ),
    I18nKey.VPN_SETTINGS_TITLE: "<b>Your SVPN settings:</b>",
    I18nKey.VPN_TRIAL_INFO: "This is a trial access until: <b>{trial_end_at}</b> (UTC).",

    I18nKey.HELP_TEXT: (
        "If you have any questions about SVPN, write to admin: @your_username (we'll replace later)."
    ),
}

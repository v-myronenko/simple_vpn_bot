from .keys import I18nKey

TRANSLATIONS = {
    I18nKey.START_WELCOME: "Welcome to SVPN 👋",
    I18nKey.START_TRIAL_INFO: "You get a 30-day trial after first use.",
    I18nKey.BTN_LANGUAGE: "🌐 Language",
    I18nKey.LANG_SELECT_PROMPT: "Choose the interface language for SVPN:",
    I18nKey.LANG_UPDATED: "Language updated. If something didn't refresh, press /start.",
    I18nKey.BTN_INSTRUCTION: "📖 How to connect VPN",
    I18nKey.INSTRUCTION_CHOOSE_DEVICE: (
        "📱 Choose your device — I'll send step-by-step instructions:"
    ),

    I18nKey.INSTRUCTION_ANDROID: (
        "📱 <b>Connect on Android</b>\n\n"
        "<b>Step 1.</b> Install <b>Hiddify</b>\n"
        "→ Google Play: search «Hiddify» or open:\n"
        "https://play.google.com/store/apps/details?id=app.hiddify.com\n\n"
        "<b>Step 2.</b> Tap the button below:\n"
        "<b>«🎁 Get trial access»</b> or <b>«🔑 My VPN access»</b>\n\n"
        "<b>Step 3.</b> The bot will send a VLESS link and QR code.\n"
        "→ Open <b>Hiddify</b>\n"
        "→ Tap <b>«+»</b> → <b>«Add from Clipboard»</b>\n"
        "(or tap «+» → «Scan QR» and scan the QR from the bot)\n\n"
        "<b>Step 4.</b> Tap the big toggle in the center of the screen\n\n"
        "✅ Done! Android will ask for VPN permission — tap «OK»."
    ),

    I18nKey.INSTRUCTION_IOS: (
        "🍎 <b>Connect on iPhone / iPad (iOS)</b>\n\n"
        "<b>Step 1.</b> Install <b>Hiddify</b>\n"
        "→ App Store: search «Hiddify Next» or open:\n"
        "https://apps.apple.com/app/hiddify-proxy-vpn/id6596777532\n\n"
        "<b>Step 2.</b> Tap the button below:\n"
        "<b>«🎁 Get trial access»</b> or <b>«🔑 My VPN access»</b>\n\n"
        "<b>Step 3.</b> The bot will send a VLESS link.\n"
        "→ Tap and hold the link → tap <b>«Copy»</b>\n"
        "→ Go back to <b>Hiddify</b>\n"
        "→ Tap <b>«+»</b> → <b>«Add from Clipboard»</b>\n\n"
        "<b>Step 4.</b> Tap the big toggle\n\n"
        "✅ Done! iOS will ask for VPN permission — tap «Allow»."
    ),

    I18nKey.INSTRUCTION_WINDOWS: (
        "💻 <b>Connect on Windows</b>\n\n"
        "<b>Step 1.</b> Download <b>Hiddify</b>\n"
        "→ Go to: https://hiddify.com\n"
        "→ Click <b>Download</b> → choose <b>Windows</b>\n"
        "→ Install and launch\n\n"
        "<b>Step 2.</b> Tap the button below:\n"
        "<b>«🎁 Get trial access»</b> or <b>«🔑 My VPN access»</b>\n\n"
        "<b>Step 3.</b> The bot will send a VLESS link.\n"
        "→ Click the link in Telegram to copy it\n"
        "→ In <b>Hiddify</b> click <b>«+»</b> → <b>«Add from Clipboard»</b>\n\n"
        "<b>Step 4.</b> Click the big toggle in the center\n\n"
        "✅ Done! VPN is active — the tray icon will light up."
    ),

    I18nKey.INSTRUCTION_MACOS: (
        "🖥 <b>Connect on macOS</b>\n\n"
        "<b>Step 1.</b> Download <b>Hiddify</b>\n"
        "→ Go to: https://hiddify.com\n"
        "→ Click <b>Download</b> → choose <b>macOS</b>\n"
        "→ Open .dmg → drag to Applications → launch\n\n"
        "<b>Step 2.</b> Tap the button below:\n"
        "<b>«🎁 Get trial access»</b> or <b>«🔑 My VPN access»</b>\n\n"
        "<b>Step 3.</b> The bot will send a VLESS link.\n"
        "→ Copy the link\n"
        "→ In <b>Hiddify</b> click <b>«+»</b> → <b>«Add from Clipboard»</b>\n\n"
        "<b>Step 4.</b> Click the big toggle\n\n"
        "✅ Done! macOS will ask permission — click «Allow». Menu bar icon = VPN on."
    ),

    I18nKey.START_ACTIVE_SUB: (
        "✅ You have an active subscription.\n\n"
        "Plan: <b>{plan_name}</b>\n"
        "Until: <b>{end_at}</b>\n"
        "Server: <b>{server_name} ({server_region})</b>\n\n"
        "Press the button below to get or refresh your connection settings."
    ),
    I18nKey.START_NO_SUB: (
        "You don't have an active SVPN subscription yet.\n\n"
        "Try «🎁 Get trial access» — 30 days free,\n"
        "or go straight to «💳 Buy subscription»."
    ),

    I18nKey.BTN_GET_VPN: "Get VPN",
    I18nKey.BTN_BUY: "💳 Buy subscription",
    I18nKey.BTN_PROFILE: "My profile",
    I18nKey.BTN_SHOW_ACCESS_ACTIVE: "🔑 My VPN access",
    I18nKey.BTN_RENEW: "🔄 Renew subscription",
    I18nKey.BTN_TRIAL: "🎁 Get trial access (30 days)",
    I18nKey.BTN_HELP: "❓ Help",

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
        "Valid until: <b>{end_at}</b>\n\n"
        "Tap «🔑 My VPN access» to get your connection config."
    ),
    I18nKey.PAYMENT_SUCCESS_GENERIC: (
        "🎉 Subscription activated! Press /start to get your config."
    ),

    I18nKey.TRIAL_EXPIRED: (
        "Your trial access is no longer available.\n\n"
        "To continue using SVPN, please purchase a subscription from the menu."
    ),
    I18nKey.VPN_FETCH_ERROR: (
        "Failed to fetch VPN configuration. "
        "Please try again later or contact support."
    ),
    I18nKey.VPN_SETTINGS_TITLE: (
        "🔑 <b>Your SVPN settings:</b>\n\n"
        "Copy the link below and paste it into Hiddify (<b>«+» → Add from Clipboard</b>),\n"
        "or scan the QR code.\n\n"
        "Haven't installed Hiddify yet? Tap «📖 How to connect VPN»."
    ),
    I18nKey.VPN_TRIAL_INFO: "⏳ This is a trial access. Valid until: <b>{trial_end_at}</b> (UTC).",

    I18nKey.HELP_TEXT: (
        "❓ <b>Need help?</b>\n\n"
        "Write to admin on Telegram: @svpnfun\n\n"
        "Also tap «📖 How to connect VPN» — step-by-step guides\n"
        "for Android, iPhone, Windows and Mac (Hiddify app)."
    ),
}
from .keys import I18nKey

TRANSLATIONS = {
    I18nKey.START_WELCOME: "Bienvenido a SVPN 👋",
    I18nKey.START_TRIAL_INFO: "Obtienes una prueba de 30 días después del primer uso.",
    I18nKey.BTN_LANGUAGE: "🌐 Idioma",
    I18nKey.LANG_SELECT_PROMPT: "Elige el idioma de la interfaz de SVPN:",
    I18nKey.LANG_UPDATED: "Idioma actualizado. Si algo no se ha actualizado, pulsa /start.",
    I18nKey.BTN_INSTRUCTION: "📖 Cómo conectar VPN",
    I18nKey.INSTRUCTION_CHOOSE_DEVICE: (
        "📱 Elige tu dispositivo — te enviaré instrucciones paso a paso:"
    ),

    I18nKey.INSTRUCTION_ANDROID: (
        "📱 <b>Conectar en Android</b>\n\n"
        "<b>Paso 1.</b> Instala <b>Hiddify</b>\n"
        "→ Google Play: busca «Hiddify» o abre:\n"
        "https://play.google.com/store/apps/details?id=app.hiddify.com\n\n"
        "<b>Paso 2.</b> Pulsa el botón de abajo:\n"
        "<b>«🎁 Obtener prueba»</b> o <b>«🔑 Mi acceso VPN»</b>\n\n"
        "<b>Paso 3.</b> El bot te enviará un enlace VLESS y QR.\n"
        "→ Abre <b>Hiddify</b>\n"
        "→ Pulsa <b>«+»</b> → <b>«Añadir desde portapapeles»</b>\n"
        "(o «+» → «Escanear QR» y escanea el QR del bot)\n\n"
        "<b>Paso 4.</b> Pulsa el gran interruptor en el centro\n\n"
        "✅ ¡Listo! Android pedirá permiso VPN — pulsa «OK»."
    ),

    I18nKey.INSTRUCTION_IOS: (
        "🍎 <b>Conectar en iPhone / iPad (iOS)</b>\n\n"
        "<b>Paso 1.</b> Instala <b>Hiddify</b>\n"
        "→ App Store: busca «Hiddify Next» o abre:\n"
        "https://apps.apple.com/app/hiddify-proxy-vpn/id6596777532\n\n"
        "<b>Paso 2.</b> Pulsa el botón de abajo:\n"
        "<b>«🎁 Obtener prueba»</b> o <b>«🔑 Mi acceso VPN»</b>\n\n"
        "<b>Paso 3.</b> El bot enviará un enlace VLESS.\n"
        "→ Mantén pulsado el enlace → pulsa <b>«Copiar»</b>\n"
        "→ Ve a <b>Hiddify</b>\n"
        "→ Pulsa <b>«+»</b> → <b>«Add from Clipboard»</b>\n\n"
        "<b>Paso 4.</b> Activa el gran interruptor\n\n"
        "✅ ¡Listo! iOS pedirá permiso VPN — pulsa «Permitir»."
    ),

    I18nKey.INSTRUCTION_WINDOWS: (
        "💻 <b>Conectar en Windows</b>\n\n"
        "<b>Paso 1.</b> Descarga <b>Hiddify</b>\n"
        "→ Web: https://hiddify.com\n"
        "→ Click <b>Download</b> → elige <b>Windows</b>\n"
        "→ Instala y abre\n\n"
        "<b>Paso 2.</b> Pulsa el botón de abajo:\n"
        "<b>«🎁 Obtener prueba»</b> o <b>«🔑 Mi acceso VPN»</b>\n\n"
        "<b>Paso 3.</b> El bot enviará el enlace VLESS.\n"
        "→ Haz clic en el enlace en Telegram para copiarlo\n"
        "→ En <b>Hiddify</b> click <b>«+»</b> → <b>«Add from Clipboard»</b>\n\n"
        "<b>Paso 4.</b> Activa el gran interruptor en el centro\n\n"
        "✅ ¡Listo! VPN activo — el ícono en la bandeja se iluminará."
    ),

    I18nKey.INSTRUCTION_MACOS: (
        "🖥 <b>Conectar en macOS</b>\n\n"
        "<b>Paso 1.</b> Descarga <b>Hiddify</b>\n"
        "→ Web: https://hiddify.com\n"
        "→ Click <b>Download</b> → elige <b>macOS</b>\n"
        "→ Abre .dmg → arrastra a Applications → abre\n\n"
        "<b>Paso 2.</b> Pulsa el botón de abajo:\n"
        "<b>«🎁 Obtener prueba»</b> o <b>«🔑 Mi acceso VPN»</b>\n\n"
        "<b>Paso 3.</b> El bot enviará el enlace VLESS.\n"
        "→ Cópialo\n"
        "→ En <b>Hiddify</b> click <b>«+»</b> → <b>«Add from Clipboard»</b>\n\n"
        "<b>Paso 4.</b> Activa el gran interruptor\n\n"
        "✅ ¡Listo! macOS pedirá permiso — click «Permitir». Ícono en la barra = VPN activo."
    ),

    I18nKey.START_ACTIVE_SUB: (
        "✅ Tienes una suscripción activa.\n\n"
        "Plan: <b>{plan_name}</b>\n"
        "Hasta: <b>{end_at}</b>\n"
        "Servidor: <b>{server_name} ({server_region})</b>\n\n"
        "Pulsa el botón de abajo para obtener o actualizar la configuración."
    ),
    I18nKey.START_NO_SUB: (
        "Todavía no tienes una suscripción activa a SVPN.\n\n"
        "Prueba «🎁 Obtener prueba» — 30 días gratis,\n"
        "o ve directo a «💳 Comprar suscripción»."
    ),

    I18nKey.BTN_GET_VPN: "Obtener VPN",
    I18nKey.BTN_BUY: "💳 Comprar suscripción",
    I18nKey.BTN_PROFILE: "Mi perfil",
    I18nKey.BTN_SHOW_ACCESS_ACTIVE: "🔑 Mi acceso VPN",
    I18nKey.BTN_RENEW: "🔄 Renovar suscripción",
    I18nKey.BTN_TRIAL: "🎁 Obtener prueba (30 días)",
    I18nKey.BTN_HELP: "❓ Ayuda",

    I18nKey.SUB_EXPIRED: "Tu suscripción ha expirado.",
    I18nKey.ERR_GENERIC: "Algo salió mal. Inténtalo de nuevo.",
    I18nKey.ERR_BACKEND: "Error al contactar con el servidor. Inténtalo más tarde.",

    I18nKey.INVOICE_TITLE: "SVPN — suscripción de 30 días",
    I18nKey.INVOICE_DESCRIPTION: (
        "Acceso a SVPN durante 30 días. Después del pago la suscripción se activará automáticamente."
    ),
    I18nKey.PAYMENT_ACTIVATING: "✅ Pago recibido. Activando tu suscripción...",
    I18nKey.PAYMENT_BACKEND_FAIL: (
        "⚠️ El pago se ha realizado, pero no pudimos confirmar la suscripción.\n"
        "Escribe al soporte y lo solucionaremos rápido."
    ),
    I18nKey.PAYMENT_SUCCESS_WITH_END: (
        "🎉 ¡Suscripción activa!\n\n"
        "Válida hasta: <b>{end_at}</b>\n\n"
        "Pulsa «🔑 Mi acceso VPN» para obtener tu configuración."
    ),
    I18nKey.PAYMENT_SUCCESS_GENERIC: (
        "🎉 Suscripción activada. Pulsa /start para obtener tu config."
    ),

    I18nKey.TRIAL_EXPIRED: (
        "Tu acceso de prueba ya no está disponible.\n\n"
        "Para seguir usando SVPN, compra una suscripción desde el menú."
    ),
    I18nKey.VPN_FETCH_ERROR: (
        "No se pudo obtener la configuración de VPN. "
        "Inténtalo más tarde o contacta con soporte."
    ),
    I18nKey.VPN_SETTINGS_TITLE: (
        "🔑 <b>Tus ajustes de SVPN:</b>\n\n"
        "Copia el enlace de abajo y pégalo en Hiddify (<b>«+» → Add from Clipboard</b>),\n"
        "o escanea el código QR.\n\n"
        "¿No tienes Hiddify? Pulsa «📖 Cómo conectar VPN»."
    ),
    I18nKey.VPN_TRIAL_INFO: "⏳ Acceso de prueba. Válido hasta: <b>{trial_end_at}</b> (UTC).",

    I18nKey.HELP_TEXT: (
        "❓ <b>¿Necesitas ayuda?</b>\n\n"
        "Escribe al admin en Telegram: @svpnfun\n\n"
        "También pulsa «📖 Cómo conectar VPN» — instrucciones paso a paso\n"
        "para Android, iPhone, Windows y Mac (app Hiddify)."
    ),
}
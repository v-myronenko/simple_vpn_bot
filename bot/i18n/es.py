from .keys import I18nKey

TRANSLATIONS = {
    I18nKey.START_WELCOME: "Bienvenido a SVPN 👋",
    I18nKey.START_TRIAL_INFO: "Obtienes una prueba de 3 días después del primer uso.",
    I18nKey.BTN_LANGUAGE: "Idioma",
    I18nKey.LANG_SELECT_PROMPT: "Elige el idioma de la interfaz de SVPN:",
    I18nKey.LANG_UPDATED: "Idioma actualizado. Si algo no se ha actualizado, pulsa /start.",

    I18nKey.START_ACTIVE_SUB: (
        "✅ Tienes una suscripción activa.\n\n"
        "Plan: <b>{plan_name}</b>\n"
        "Hasta: <b>{end_at}</b>\n"
        "Servidor: <b>{server_name} ({server_region})</b>\n\n"
        "Pulsa el botón de abajo para obtener o actualizar la configuración de conexión."
    ),
    I18nKey.START_NO_SUB: (
        "Todavía no tienes una suscripción activa a SVPN.\n\n"
        "Pulsa el botón de abajo para elegir un plan y suscribirte."
    ),

    I18nKey.BTN_GET_VPN: "Obtener VPN",
    I18nKey.BTN_BUY: "Comprar suscripción",
    I18nKey.BTN_PROFILE: "Mi perfil",
    I18nKey.BTN_SHOW_ACCESS_ACTIVE: "Mi acceso VPN",
    I18nKey.BTN_RENEW: "Renovar suscripción",
    I18nKey.BTN_TRIAL: "Obtener prueba",
    I18nKey.BTN_HELP: "Ayuda",

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
        "Válida hasta: <b>{end_at}</b>"
    ),
    I18nKey.PAYMENT_SUCCESS_GENERIC: (
        "🎉 Suscripción activada. (Los detalles se actualizarán en /start)"
    ),

    I18nKey.TRIAL_EXPIRED: (
        "Tu acceso de prueba ya no está disponible.\n\n"
        "Para seguir usando SVPN, compra una suscripción desde el menú."
    ),
    I18nKey.VPN_FETCH_ERROR: (
        "No se pudo obtener la configuración de VPN. "
        "Inténtalo más tarde o contacta con soporte."
    ),
    I18nKey.VPN_SETTINGS_TITLE: "<b>Tus ajustes de SVPN:</b>",
    I18nKey.VPN_TRIAL_INFO: "Este es un acceso de prueba hasta: <b>{trial_end_at}</b> (UTC).",

    I18nKey.HELP_TEXT: (
        "Si tienes preguntas sobre SVPN, escribe al admin: @your_username (lo cambiaremos más tarde)."
    ),
}

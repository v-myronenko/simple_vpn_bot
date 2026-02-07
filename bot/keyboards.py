from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from i18n.keys import I18nKey


def get_main_menu_keyboard(
    has_active_subscription: bool,
    i18n,
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if has_active_subscription:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=i18n.t(I18nKey.BTN_SHOW_ACCESS_ACTIVE),
                    callback_data="show_access",
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=i18n.t(I18nKey.BTN_RENEW),
                    callback_data="renew_subscription",
                )
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=i18n.t(I18nKey.BTN_TRIAL),
                    callback_data="show_access",
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=i18n.t(I18nKey.BTN_BUY),
                    callback_data="buy_subscription",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=i18n.t(I18nKey.BTN_HELP),
                callback_data="help",
            )
        ]
    )

    # 🌐 Кнопка вибору мови
    buttons.append(
        [
            InlineKeyboardButton(
                text=i18n.t(I18nKey.BTN_LANGUAGE),
                callback_data="language",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_language_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang:ua")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")],
        [InlineKeyboardButton(text="🇪🇸 Español", callback_data="set_lang:es")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

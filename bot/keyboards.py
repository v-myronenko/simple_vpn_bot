from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard(has_active_subscription: bool) -> InlineKeyboardMarkup:
    buttons = []

    if has_active_subscription:
        buttons.append(
            [InlineKeyboardButton(text="Мій VPN доступ", callback_data="show_access")]
        )
        buttons.append(
            [InlineKeyboardButton(text="Продовжити підписку", callback_data="renew_subscription")]
        )
    else:
        buttons.append(
            [InlineKeyboardButton(text="Купити підписку", callback_data="buy_subscription")]
        )

    buttons.append(
        [InlineKeyboardButton(text="Допомога", callback_data="help")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

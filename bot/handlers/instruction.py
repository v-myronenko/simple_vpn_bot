from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from i18n.keys import I18nKey
from services.locale_service import LocaleService

router = Router()


@router.callback_query(F.data == "instruction")
async def instruction_menu(callback: CallbackQuery, i18n):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📱 Android", callback_data="inst_android"),
            InlineKeyboardButton(text="🍎 iOS", callback_data="inst_ios"),
        ],
        [
            InlineKeyboardButton(text="💻 Windows", callback_data="inst_windows"),
            InlineKeyboardButton(text="🖥 macOS", callback_data="inst_macos"),
        ],
    ])
    await callback.message.edit_text(
        i18n.t(I18nKey.INSTRUCTION_CHOOSE_DEVICE),
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "inst_android")
async def inst_android(callback: CallbackQuery, i18n):
    await callback.message.edit_text(
        i18n.t(I18nKey.INSTRUCTION_ANDROID),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "inst_ios")
async def inst_ios(callback: CallbackQuery, i18n):
    await callback.message.edit_text(
        i18n.t(I18nKey.INSTRUCTION_IOS),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "inst_windows")
async def inst_windows(callback: CallbackQuery, i18n):
    await callback.message.edit_text(
        i18n.t(I18nKey.INSTRUCTION_WINDOWS),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "inst_macos")
async def inst_macos(callback: CallbackQuery, i18n):
    await callback.message.edit_text(
        i18n.t(I18nKey.INSTRUCTION_MACOS),
        parse_mode="HTML",
    )
    await callback.answer()
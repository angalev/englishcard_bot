from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль')],
    [KeyboardButton(text='Настройки')],
    [KeyboardButton(text='О нас')]
], is_persistent=True)

start_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать игру', callback_data='start_game')]
])

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Погугли', url='https://www.google.ru/')]
])


async def play_buttons(random_words: list):
    keyboard = ReplyKeyboardBuilder()
    for eng_word in random_words[0]:
        keyboard.add(KeyboardButton(text=eng_word))
    keyboard.add(KeyboardButton(text='Дальше ⏩'))
    keyboard.add(KeyboardButton(text='Добавить слово ➕'))
    keyboard.add(KeyboardButton(text='Удалить слово 🔙'))
    return keyboard.adjust(2).as_markup()

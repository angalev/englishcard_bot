import random

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from random import shuffle


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль')],
    [KeyboardButton(text='Настройки')],
    [KeyboardButton(text='О нас')],
    [KeyboardButton(text='Назад')]
], is_persistent=True)

personal_settings = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Избранные слова')],
    [KeyboardButton(text='Слова из словаря')],
    [KeyboardButton(text='Назад')]
], is_persistent=True)

start_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать игру', callback_data='start_game')]
])

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Погугли', url='https://www.google.ru/')]
])

async def play_buttons(random_words: list):
    keyboard = ReplyKeyboardBuilder()
    shuffled_buttons = []
    for eng_word in random_words[0]:
        shuffled_buttons.append(KeyboardButton(text=eng_word))
    random.shuffle(shuffled_buttons)
    keyboard.add(*shuffled_buttons)
    keyboard.add(KeyboardButton(text='Дальше ⏩'))
    keyboard.add(KeyboardButton(text='Добавить слово ➕'))
    keyboard.add(KeyboardButton(text='Главное меню'))
    keyboard.add(KeyboardButton(text='Удалить слово 🔙'))
    return keyboard.adjust(2).as_markup()

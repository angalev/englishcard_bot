import random

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.keyboards import settings, start_menu, play_buttons, main, personal_settings
from app.text_messages import start_message

import app.database.requests as rq

router = Router()

class Play(StatesGroup):
    play = State()
    favourite_words = State()

#Наполнение базы данных словами из англо-русского словаря
@router.startup()
async def fill_database():
    await rq.fill_vocabulary()

# Тестовый функционал команды help
@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это тебе поможет', reply_markup=settings)
#Запуск игрового меню при команде старт
@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(start_message, reply_markup=start_menu)
#Обработка команды 'Назад'
@router.message(F.text=='Назад')
async def restart(message: Message):
    await message.answer(start_message, reply_markup=start_menu)
#Обработка команды 'Настройки'
@router.message(F.text=='Настройки')
async def restart(message: Message):
    await message.answer('Выберите режим игры:', reply_markup=personal_settings)
#Генерация вопросов с использованием случайных слов из загруженного англо-русского словаря
@router.message(F.text=='Слова из словаря')
async def start_game(message: Message, state: FSMContext):
    await state.set_state(Play.play)
    await start_new_round(message=message, state=state)
#Генерация вопросов с использованием случайных слов из избранных в базе данных.
# Выбирается одно слово, остальные 3 загружаются из словаря
@router.message(F.text=='Избранные слова')
async def start_game(message: Message, state: FSMContext):
    await state.set_state(Play.favourite_words)
    await start_favourites(message=message, state=state)
#Функция игры при выборе в настройках сценария с изучением избранных пользователем слов
async def start_favourites(message: Message, state: FSMContext):
    # Генерируем новые слова и вопрос
    random_words = await rq.get_favourite_words(message.from_user.id)
    correct_answer = random_words[0][3]
    # Сохраняем данные в состоянии
    await state.update_data(
        random_words=random_words,
        correct_answer=correct_answer
    )
    # Отправляем вопрос пользователю
    await message.answer(
        f'Выбери правильный перевод слова:\n 🇷🇺{random_words[1][3]}',
        reply_markup=await play_buttons(random_words)
    )

# Функция игры с изучением случайных слов из общего англо-русского словаря
async def start_new_round(message: Message, state: FSMContext):
    # Генерируем новые слова и вопрос
    random_words = await rq.get_words()
    correct_answer = random_words[0][3]
    # Сохраняем данные в состоянии
    await state.update_data(
        random_words=random_words,
        correct_answer=correct_answer
    )
    # Отправляем вопрос пользователю
    await message.answer(
        f'Выбери правильный перевод слова:\n 🇷🇺{random_words[1][3]}',
        reply_markup=await play_buttons(random_words)
    )
#Старт игры при нажатии кнопки в инлайн запросе под приветственным сообщением
@router.callback_query(F.data=='start_game')
async def start_game(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Play.play)
    await start_new_round(message=callback.message, state=state)
#Выводит на экран бота кнопки главного меню с настройками
async def main_menu(message: Message):
    await message.answer('Вы находитесь в главном меню', reply_markup=main)
# Основная логика игры с применением слов из общего словаря
@router.message(Play.play)
async def check_correct_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['correct_answer'] == message.text:
        await message.answer('✅Правильно!')
        # Запускаем новый раунд
        await start_new_round(message, state)
    elif message.text == 'Дальше ⏩':
        await start_new_round(message, state)
    elif message.text == 'Добавить слово ➕':
        await rq.add_to_favourites(user_id=message.from_user.id,
                                   word_id=data['random_words'][2][3])
    elif message.text == 'Удалить слово 🔙':
        if await rq.dell_from_favourites(user_id=message.from_user.id,
                                   word_id=data['random_words'][2][3]):
            await message.answer('🗑Слово удалено из базы!')
        else:
            await message.answer('🤷‍♂️Слово не найдено в базе!')
    elif message.text == 'Главное меню':
        await state.clear()
        await main_menu(message)
    else:
        await message.answer('❌Неправильно, попробуй ещё раз❌')
#Основная логика игры с применением слов, избранных пользователем
@router.message(Play.favourite_words)
async def check_correct_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['correct_answer'] == message.text:
        await message.answer('✅Правильно!')
        # Запускаем новый раунд
        await start_favourites(message, state)
    elif message.text == 'Дальше ⏩':
        await start_favourites(message, state)
    elif message.text == 'Добавить слово ➕':
        await rq.add_to_favourites(user_id=message.from_user.id,
                                   word_id=data['random_words'][2][3])
    elif message.text == 'Удалить слово 🔙':
        if await rq.dell_from_favourites(user_id=message.from_user.id,
                                   word_id=data['random_words'][2][3]):
            await message.answer('🗑Слово удалено из базы!')
        else:
            await message.answer('🤷‍♂️Слово не найдено в базе!')
    elif message.text == 'Главное меню':
        await state.clear()
        await main_menu(message)
    else:
        await message.answer('❌Неправильно, попробуй ещё раз❌')
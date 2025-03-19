import random

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.keyboards import settings, start_menu, play_buttons, main
from app.text_messages import start_message

import app.database.requests as rq

router = Router()

class Play(StatesGroup):
    play = State()


@router.startup()
async def fill_database():
    await rq.fill_vocabulary()

@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это тебе поможет', reply_markup=settings)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(start_message, reply_markup=start_menu)

# Выносим логику старта игры в отдельную функцию
async def start_new_round(message: Message, state: FSMContext):
    # Генерируем новые слова и вопрос
    random_words = await rq.get_words()
    random_question = random.randrange(4)
    correct_answer = random_words[0][random_question]
    # Сохраняем данные в состоянии
    await state.update_data(
        random_words=random_words,
        random_question=random_question,
        correct_answer=correct_answer
    )
    # Отправляем вопрос пользователю
    await message.answer(
        f'Выбери правильный перевод слова:\n 🇷🇺{random_words[1][random_question]}',
        reply_markup=await play_buttons(random_words)
    )

@router.callback_query(F.data=='start_game')
async def start_game(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Play.play)
    await start_new_round(message=callback.message, state=state)

@router.message(Play.play)
async def check_correct_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    # await start_new_round(message, state)
    if data['correct_answer'] == message.text:
        await message.answer('✅Правильно!')
        # Запускаем новый раунд
        await start_new_round(message, state)
    elif message.text == 'Дальше ⏩':
        await start_new_round(message, state)
    elif message.text == 'Добавить слово ➕':
        await rq.add_to_favourites(user_id=message.from_user.id,
                                   word_id=data['random_words'][2][data['random_question']])
    elif message.text == 'Удалить слово 🔙':
        await rq.dell_from_favourites(user_id=message.from_user.id,
                                   word_id=data['random_words'][2][data['random_question']])
    else:
        await message.answer('❌Неправильно, попробуй ещё раз❌')


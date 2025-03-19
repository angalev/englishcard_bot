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

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(start_message, reply_markup=start_menu)

@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это тебе поможет', reply_markup=settings)

@router.callback_query(F.data=='start_game')
async def start_game(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Play.play)
    random_words = await rq.get_words()
    random_question = random.randrange(4)
    correct_answer = random_words[0][random_question]
    await state.update_data(random_words=random_words,
                            random_question=random_question,
                            correct_answer=correct_answer)
    await callback.answer(f'Выбери правильный перевод слова:{random_words[1][random_question]}')
    await callback.message.answer(f'Выбери правильный перевод слова:{random_words[1][random_question]}',
                                  reply_markup=await play_buttons(random_words))

@router.message(Play.play)
async def if_correct(message: Message):
    user_answer = message.text
    if correct_answer == user_answer:
        random_words = await rq.get_words()
        random_question = random.randrange(4)
        correct_answer = random_words[0][random_question]
        await message.answer(f'Выбери правильный перевод слова:{random_words[1][random_question]}',
                                      reply_markup=await play_buttons(random_words))
    else:
        print('zalupakonya')

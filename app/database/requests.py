import json
import random

from app.database.models import async_session
from app.database.models import User, Word
from sqlalchemy import select, func

from dotenv import load_dotenv
load_dotenv()

async def set_user(tg_user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_user_id == tg_user_id))

        if not user:
            session.add(User(tg_user_id=tg_user_id))
            await session.commit()

async def fill_vocabulary() -> None:
    async with async_session() as session:
        word = await session.scalar(select(Word))
        if not word:
            with open('app/database/JSONdict.txt', encoding='UTF-8', mode='r') as f:
                data = json.load(f)
            for word_pair in data:
                if len(word_pair['word'].split()) == 1 and len(word_pair['translates'][0].split()) == 1:
                    session.add(Word(eng_word=word_pair['word'][:25], rus_word=word_pair['translates'][0][:25]))
            await session.commit()

async def get_words() -> list:
    async with async_session() as session:
        total_words_number = await session.scalar(select(func.max(Word.id)))
        random_words = random.sample(range(1, total_words_number + 1), k=4)
        words = [[], []]
        for word_id in random_words:
            result = await session.scalar(select(Word).where(Word.id == word_id))
            words[0].append(result.eng_word)
            words[1].append(result.rus_word)
        return words


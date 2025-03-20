import json
import random

from sqlalchemy.exc import SQLAlchemyError

from app.database.models import async_session
from app.database.models import User, Word, UserWord
from sqlalchemy import select, func

from dotenv import load_dotenv
load_dotenv()

async def set_user(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))

        if not user:
            session.add(User(user_id=user_id))
            await session.commit()

async def add_to_favourites(user_id, word_id):
    async with async_session() as session:
        user_word = await session.scalar(select(UserWord).where(UserWord.word_id == word_id).where(
            UserWord.user_id == user_id))

        if not user_word:
            session.add(UserWord(user_id=user_id, word_id=word_id))
            await session.commit()

async def dell_from_favourites(user_id, word_id):
    async with async_session() as session:
        try:
            user_word = await session.scalar(
                select(UserWord).where(
                    UserWord.word_id == word_id,
                    UserWord.user_id == user_id
                )
            )

            if user_word:
                print(f"Deleting UserWord: {user_word.word_id}")
                await session.delete(user_word)
                await session.commit()
                return True
            else:
                print("UserWord not found.")
                return False
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}")
            await session.rollback()
            return False


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


async def get_favourite_words(user_id) -> list:
    async with async_session() as session:
        random_words = await session.execute(
            select(Word)
            .order_by(func.random())
            .limit(3)
        )
        random_words = random_words.scalars().all()

        word_from_favourite = await session.execute(
            select(Word)
            .join(UserWord)
            .where(UserWord.user_id == user_id)
            .order_by(func.random())
            .limit(1)
        )
        word_from_favourite = word_from_favourite.scalars().first()
        words = [[], [], []]
        for word in random_words:
            words[0].append(word.eng_word)
            words[1].append(word.rus_word)
            words[2].append(word.id)
        if word_from_favourite:
            words[0].append(word_from_favourite.eng_word)
            words[1].append(word_from_favourite.rus_word)
            words[2].append(word_from_favourite.id)
        return words

async def get_words() -> list:
    async with async_session() as session:
        total_words_number = await session.scalar(select(func.max(Word.id)))
        random_words = random.sample(range(1, total_words_number + 1), k=4)
        words = [[], [], []]
        for word_id in random_words:
            result = await session.scalar(select(Word).where(Word.id == word_id))
            words[0].append(result.eng_word)
            words[1].append(result.rus_word)
            words[2].append(result.id)
        return words


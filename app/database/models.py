import os

from sqlalchemy import String, BigInteger, Boolean, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dotenv import load_dotenv


load_dotenv()
engine = create_async_engine(url=f'postgresql+asyncpg://{os.getenv("USER")}:{os.getenv("PASSWORD")}@localhost:5432/{os.getenv("DBNAME")}')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class UserWord(Base):
    __tablename__ = 'users_words'

    word_id: Mapped[int] = mapped_column(ForeignKey('words.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), primary_key=True)
    favourites: Mapped[bool] = mapped_column(Boolean, nullable=True)
    user: Mapped['User'] = relationship(back_populates='word_associations')
    word: Mapped['Word'] = relationship(back_populates='user_associations')

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    word_associations: Mapped[list['UserWord']] = relationship(back_populates='user')
    words: Mapped[list['Word']] = relationship(
        secondary='users_words',
        viewonly=True,
        back_populates='users'
    )

class Word(Base):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    eng_word: Mapped[str] = mapped_column(String(25))
    rus_word: Mapped[str] = mapped_column(String(25))
    user_associations: Mapped[list['UserWord']] = relationship(back_populates='word')
    users: Mapped[list['User']] = relationship(
        secondary='users_words',
        viewonly=True,
        back_populates='words'
    )


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




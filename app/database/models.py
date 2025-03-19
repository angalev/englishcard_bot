import os

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dotenv import load_dotenv


load_dotenv()
engine = create_async_engine(url=f'postgresql+asyncpg://{os.getenv("USER")}:{os.getenv("PASSWORD")}@localhost:5432/{os.getenv("DBNAME")}')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger)

class Word(Base):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    eng_word: Mapped[str] = mapped_column(String(25))
    rus_word: Mapped[str] = mapped_column(String(25))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




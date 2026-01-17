from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase
import logging

from application.config import settings

logger = logging.getLogger(__name__)

class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all ORM models."""
    pass

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # Логируем SQL-запросы в режиме отладки
    pool_pre_ping=True,  # Проверяем соединение перед использованием
    pool_size=20,        # Максимальное количество соединений в пуле
    max_overflow=10,     # Максимальное количество дополнительных соединений сверх pool_size
)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,            # autoflush: НЕ автоматически flush перед SELECT запросами
    autocommit=False,
)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency для получения БД сессии.

    Используется в endpoints:
    ```python
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        # db это асинхронная сессия
        # FastAPI автоматически закроет её после endpoint'а
    ```

    Процесс:
    1. FastAPI вызывает get_db()
    2. Создаётся новая AsyncSession
    3. Выдаётся endpoint'у
    4. Endpoint работает
    5. FastAPI вызывает finally блок (закрывает сессию)
    6. Если была ошибка - rollback
    """

    async with async_session_maker() as session:
        # async with: автоматически закроет сессию
        # Даже если будет exception

        try:
            yield session
            # yield: даём сессию endpoint'у
            # Процесс приостанавливается тут
            # Endpoint работает...
            # После endpoint'а процесс возобновляется

        except Exception:
            # Если в endpoint'е была ошибка
            await session.rollback()
            # Откатываем все изменения в БД
            raise

        finally:
            # Закрываем сессию в любом случае
            # (успех или ошибка)
            await session.close()


async def dispose_db():
    """
    Закрывает все соединения в engine'е.

    Используется при shutdown приложения:
    ```python
    @app.on_event("shutdown")
    async def shutdown():
        await dispose_db()
    ```

    Это важно потому что:
    - Соединения остаются в памяти
    - Если не закрыть - утечка памяти
    - При перезапуске приложения - конфликты
    """

    await engine.dispose()
    logger.info("Database connections disposed")



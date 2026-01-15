"""
Конфигурация приложения используя Pydantic Settings.

Pydantic Settings автоматически:
- Загружает переменные из .env
- Валидирует типы
- Предоставляет default значения
- Кеширует значения для production

Это лучше чем читать os.getenv() везде по коду,
потому что:
1. Типобезопасность
2. Валидация при запуске
3. IDE может подсказывать поля
4. Документация в одном месте
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Главная конфигурация приложения.

    Все поля по умолчанию загружаются из переменных окружения.

    Например:
    - DATABASE_URL → settings.database_url
    - JWT_SECRET_KEY → settings.jwt_secret_key
    - Etc.
    """

    # ========== DATABASE ==========
    database_url: str = Field(..., alias="DATABASE_URL")
    # alias: в .env используем DATABASE_URL, но в коде database_url
    # ... означает что это обязательное поле
    api_key: str = Field(..., alias="API_KEY")
    campaign_id: int = Field(..., alias="CAMPAIGN_ID")
    business_id: int = Field(..., alias="BUSINESS_ID")



    class Config:
        env_file = "C:\\Users\\DemTiOset\\PycharmProjects\\Gorbushka_Keepers\\.env"
        case_sensitive = False
        # Не требует точного совпадения регистра
        # DATABASE_url, database_url, DATABASE_URL - всё работает


# Создаём глобальный объект settings
# Используем везде в приложении: from config import settings
settings = Settings()


"""Конфигурация и параметры приложения.

Модуль для загрузки и управления переменными окружения,
включая конфигурацию бота и параметры каналов.
"""

from dataclasses import dataclass
from environs import Env


@dataclass
class ChannalSet:
    """Конфигурация канала Telegram.
    
    Атрибуты:
        id (int): Уникальный числовой ID канала
        url (str): URL канала для ссылок и перенаправлений
    """
    id: int
    url: str


@dataclass
class TgBot:
    """Конфигурация Telegram бота.
    
    Атрибуты:
        token (str): API токен бота для аутентификации в Telegram
        admin_ids (list[int]): Список Telegram ID администраторов бота
    """
    token: str
    admin_ids: list[int]


@dataclass
class Config:
    """Главная конфигурация приложения.
    
    Атрибуты:
        bot (TgBot): Конфигурация Telegram бота
        channal (ChannalSet): Конфигурация канала
    """
    bot: TgBot
    channal: ChannalSet


def load_config(path: str | None = None) -> Config:
    """Загружает конфигурацию из переменных окружения.
    
    Читает файл .env и извлекает используемые переменные:
    - BOT_TOKEN: API токен Telegram бота
    - ADMIN_IDS: Запятая-разделённый список ID администраторов
    - CHANNEL_ID: Числовой ID канала
    - CHANNEL_URL: URL канала
    
    Параметры:
        path (str | None): Путь к файлу .env. 
                          Если None, использует .env в текущей директории.
    
    Возвращает:
        Config: Объект конфигурации с загруженными параметрами
    
    Примеры .env файла:
        BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
        ADMIN_IDS=123456789,987654321
        CHANNEL_ID=-1001234567890
        CHANNEL_URL=https://t.me/mychannel
    """

    env: Env = Env()
    env.read_env(path)

    return Config(
        bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))
        ),
        channal=ChannalSet(
            id=env.int('CHANNEL_ID'),
            url=env('CHANNEL_URL')
        ),
    )
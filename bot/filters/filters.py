"""Фильтры для обработчиков aiogram.

Модуль содержит пользовательские фильтры для проверки различных условий,
таких как тип чата, наличие подписки и прав администратора.
"""

from datetime import datetime
from typing import Union

from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from db.database import AsyncSessionLocal
from db.requests_db import UserRepository


class IsPrivateChat(BaseFilter):
    """Фильтр для проверки, что сообщение отправлено в личный чат.
    
    Используется для обработки команд только в личных сообщениях боту,
    без срабатывания в групповых чатах.
    
    Возвращает:
        bool: True если чат приватный (personal), иначе False
    
    Пример:
        @router.message(Command("start"), IsPrivateChat())
        async def cmd_start(message: Message):
            pass
    """

    async def __call__(self, message: Message) -> bool:
        return message.chat.type == "private"


class IsHavePodpiska(BaseFilter):
    """Фильтр для проверки активной подписки пользователя.
    
    Проверяет, находится ли подписка пользователя в силе,
    сравнивая текущую дату/время с датой окончания подписки.
    
    Возвращает:
        bool: True если подписка активна, иначе False
        False также возвращается если пользователь не найден в БД
    
    Примечания:
        - Требует асинхронного доступа к БД
        - Проверяет subscription_until > текущее время
    """

    async def __call__(self, message: Message) -> bool:
        async with AsyncSessionLocal() as session:
            user = await UserRepository.get_user_by_tg_id(
                session, message.from_user.id
            )
            if not user:
                return False
            return user.subscription_until > datetime.now()


class AdminFilter(BaseFilter):
    """Фильтр для проверки прав администратора.
    
    Проверяет, находится ли Telegram ID отправителя в списке admin_ids.
    Защищает административные команды от использования обычными пользователями.
    
    Параметры:
        event (Union[Message, CallbackQuery]): Событие Telegram (сообщение или callback)
        admin_ids (list[int]): Список Telegram ID администраторов
    
    Возвращает:
        bool: True если пользователь администратор, иначе False
    
    Примечания:
        - admin_ids передаются через dp.start_polling()
        - Работает с сообщениями и callback-кнопками
    """

    async def __call__(
        self, event: Union[Message, CallbackQuery], admin_ids: list[int]
    ) -> bool:
        return event.from_user.id in admin_ids
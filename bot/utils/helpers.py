"""Вспомогательные функции для управления пользователями.

Этот модуль содержит утилиты для работы с пользователями,
включая генерацию хешей и создание/получение профилей.
"""

import hashlib
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from db.requests_db import UserRepository


def generate_user_hash(tg_id: int) -> str:
    """Генерирует уникальный хеш для пользователя на основе его Telegram ID.
    
    Использует алгоритм SHA256 для создания 64-символьного хеша.
    Этот хеш служит уникальной реферальной ссылкой для пользователя.
    
    Параметры:
        tg_id (int): Telegram ID пользователя
    
    Возвращает:
        str: 64-символьный хеш SHA256 в шестнадцатеричном формате
    
    Пример:
        hash = generate_user_hash(123456789)
        # Returns: 'abc123...xyz789' (64 символа)
    """
    return hashlib.sha256(str(tg_id).encode()).hexdigest()[:12]


# Размер награды за успешный реферал (в монетах)
REFERRAL_BONUS = 1


async def get_or_create_user(
    session: AsyncSession, 
    tg_id: int, 
    username: Optional[str] = None,
    invited_by_hash: Optional[str] = None,
) -> dict:
    """Получает существующего пользователя или создаёт нового с отслеживанием реферала.
    
    Функция проверяет наличие пользователя в БД по Telegram ID.
    Если пользователь не найден:
    1. Генерирует уникальный хеш (SHA256 от tg_id)
    2. Проверяет валидность реферального хеша
    3. Валидирует, что пользователь не приглашает себя
    4. Создаёт пользователя с начальным балансом (2 монеты)
    5. Увеличивает счётчик приглашений у приглашающего
    6. Выплачивает награду приглашающему
    
    Параметры:
        session (AsyncSession): Асинхронная сессия базы данных
        tg_id (int): Telegram ID пользователя
        username (Optional[str]): Username Telegram пользователя, по умолчанию None
        invited_by_hash (Optional[str]): SHA256 хеш приглашающего, по умолчанию None
    
    Возвращает:
        dict: Словарь с данными пользователя:
            - id: Уникальный ID в системе
            - tg_id: Telegram ID
            - username: Username пользователя
            - coins: Текущий баланс монет
            - user_hash: Уникальный хеш пользователя
            - invited_count: Количество приглашённых
            - subscription_until: Дата окончания подписки
            - invited_by_hash: Хеш приглашающего (если был приглашен)
    
    Примечания:
        - Новый пользователь получает 2 монеты по умолчанию
        - Подписка даётся на 3 дня при регистрации
        - При наличии валидного реферального хеша:
          * Счётчик приглашений увеличивается
          * Приглашающий получает REFERRAL_BONUS (1 монету)
        - Пользователь не может пригласить себя (валидация по хешу)
    """
    user = await UserRepository.get_user_by_tg_id(session, tg_id)

    if not user:
        user_hash = generate_user_hash(tg_id)
        
        # Check if invited_by_hash is valid (user with this hash exists)
        inviter = None
        if invited_by_hash:
            inviter = await UserRepository.get_user_by_hash(session, invited_by_hash)
            
            # Валидация: пользователь не может приглашать себя
            if inviter and inviter.user_hash == user_hash:
                inviter = None
        
        # Create user with referral tracking
        user = await UserRepository.create_user(
            session=session,
            tg_id=tg_id,
            user_hash=user_hash,
            username=username,
            invited_by_hash=inviter.user_hash if inviter else None,
        )
        
        # Increment inviter's invited count and give reward
        if inviter:
            await UserRepository.increment_invited_count(session, inviter.id)
            await UserRepository.add_coins(session, inviter.id, REFERRAL_BONUS)

    return {
        "id": user.id,
        "tg_id": user.tg_id,
        "username": user.username,
        "coins": user.coins,
        "user_hash": user.user_hash,
        "invited_count": user.invited_count,
        "subscription_until": user.subscription_until,
        "invited_by_hash": user.invited_by_hash,
    }


async def process_referral_payment(
    session: AsyncSession,
    user_id: int,
    coins_to_add: int,
    days_to_add: int,
    payment_amount: float,
) -> dict:
    """Обрабатывает платеж пользователя и начисляет реферальное вознаграждение пригласившему.
    
    Функция:
    1. Добавляет монеты пользователю
    2. Продлевает подписку пользователя
    3. Находит пригласившего пользователя (реферала)
    4. Начисляет процент от суммы платежа пригласившему
    
    Параметры:
        session (AsyncSession): Асинхронная сессия базы данных
        user_id (int): ID пользователя, совершившего платеж
        coins_to_add (int): Количество монет для добавления
        days_to_add (int): Количество дней подписки для добавления
        payment_amount (float): Сумма платежа пользователя
    
    Возвращает:
        dict: Словарь с результатами операции:
            - success: bool - Успешность операции
            - user_coins_added: int - Добавленные монеты пользователю
            - user_days_added: int - Добавленные дни подписки
            - referrer_bonus: float - Начисленное вознаграждение пригласившему (если есть)
            - referrer_id: int - ID пригласившего (если есть)
    """
    # Получаем пользователя
    user = await UserRepository.get_user_by_id(session, user_id)
    if not user:
        return {
            "success": False,
            "error": "User not found"
        }
    
    # Добавляем монеты пользователю
    updated_user = await UserRepository.add_coins(session, user_id, coins_to_add)
    if not updated_user:
        return {
            "success": False,
            "error": "Failed to add coins to user"
        }
    
    # Продлеваем подписку пользователя
    updated_user = await UserRepository.extend_subscription(session, user_id, days_to_add)
    if not updated_user:
        return {
            "success": False,
            "error": "Failed to extend user subscription"
        }
    
    result = {
        "success": True,
        "user_coins_added": coins_to_add,
        "user_days_added": days_to_add,
        "referrer_bonus": 0,
        "referrer_id": None
    }
    
    # Проверяем, есть ли у пользователя пригласивший
    if user.invited_by_hash:
        # Находим пригласившего пользователя
        referrer = await UserRepository.get_user_by_hash(session, user.invited_by_hash)
        if referrer:
            # Рассчитываем вознаграждение (процент от суммы платежа)
            bonus_amount = int(payment_amount * referrer.referral_percentage / 100)
            
            # Начисляем вознаграждение пригласившему
            updated_referrer = await UserRepository.add_referral_earnings(session, referrer.id, bonus_amount)
            if updated_referrer:
                result["referrer_bonus"] = bonus_amount
                result["referrer_id"] = referrer.id
    
    return result

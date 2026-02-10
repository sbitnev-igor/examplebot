"""Обработчики пользовательских команд бота.

Этот модуль содержит асинхронные обработчики для всех пользовательских команд,
включая регистрацию, просмотр профиля, проверку баланса и справку.
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db.database import AsyncSessionLocal
from db.requests_db import UserRepository
from lexicon.lexicon import USER_LEXICON
from filters.filters import IsPrivateChat
from utils.helpers import get_or_create_user

router = Router(name="user_router")

@router.message(Command("start"), IsPrivateChat())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """Обработчик команды /start - регистрация или вход пользователя.
    
    Обрабатывает начальную команду с опциональным реферальным хешем.
    При первом входе создаёт пользователя с уникальным SHA256 хешем.
    Если передан реферальный код - связывает с приглашающим и 
    увеличивает счётчик приглашений у приглашающего.
    
    Параметры:
        message (types.Message): Telegram сообщение с командой /start
        state (FSMContext): Контекст конечного автомата
    
    Возвращает:
        None: Отправляет приветственное сообщение
    
    Пример:
        /start                    # Обычная регистрация
        /start abc123...xyz       # Регистрация по реферальной ссылке
    """
    await state.clear()
    
    # Extract referral hash from deep link (format: /start hash_value)
    invited_by_hash = None
    if message.text and len(message.text.split()) > 1:
        invited_by_hash = message.text.split()[1]
    
    async with AsyncSessionLocal() as session:
        user_data = await get_or_create_user(
            session, 
            message.from_user.id, 
            message.from_user.username,
            invited_by_hash=invited_by_hash,
        )

        text = USER_LEXICON["user_start"].format(
            hash=user_data["user_hash"][:12],
            coins=user_data["coins"]
        )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("profile"), IsPrivateChat())
async def cmd_profile(message: types.Message) -> None:
    """Обработчик команды /profile - просмотр профиля пользователя.
    
    Выводит подробную информацию профиля, включающую:
    - Уникальный ID в системе
    - Telegram ID пользователя
    - Текущий баланс монет
    - Количество приглашённых пользователей
    - Информацию о пригласившем (если применимо)
    
    Параметры:
        message (types.Message): Telegram сообщение с командой /profile
    
    Возвращает:
        None: Отправляет информацию профиля или ошибку
    """
    async with AsyncSessionLocal() as session:
        user = await UserRepository.get_user_by_tg_id(session, message.from_user.id)

        if not user:
            await message.answer("❌ Пользователь не найден")
            return

        invited_by_info = f"🔗 Приглашен: {user.invited_by_hash[:12]}..." if user.invited_by_hash else "🔗 Приглашен: Нет"
        
        text = USER_LEXICON["user_profile"].format(
            id=user.id,
            tg_id=user.tg_id,
            user_hash=user.user_hash[:12],
            coins=user.coins,
            invited=user.invited_count,
            referral_earnings=user.referral_earnings,
        ) + f"\n{invited_by_info}"
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("balance"), IsPrivateChat())
async def cmd_balance(message: types.Message) -> None:
    """Обработчик команды /balance - проверка баланса монет.
    
    Показывает текущий баланс монет пользователя в системе.
    Монеты являются внутренней валютой бота и используются
    для совершения различных операций.
    
    Параметры:
        message (types.Message): Telegram сообщение с командой /balance
    
    Возвращает:
        None: Отправляет текущий баланс или ошибку"""
    async with AsyncSessionLocal() as session:
        user = await UserRepository.get_user_by_tg_id(session, message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return

        text = f"💰 Баланс: {user.coins} монет"
    await message.answer(text)


@router.message(Command("referrals"), IsPrivateChat())
async def cmd_referrals(message: types.Message) -> None:
    """Обработчик команды /referrals - список рефералов пользователя.
    
    Выводит список пользователей, приглашённых текущим пользователем.
    Для каждого реферала показывается:
    - Telegram ID
    - Текущий баланс монет
    
    Список ограничен 30 рефералами на странице.
    Остаток показывается в виде "и ещё X рефералов".
    
    Параметры:
        message (types.Message): Telegram сообщение с командой /referrals
    
    Возвращает:
        None: Отправляет список рефералов или уведомление об их отсутствии
    """
    async with AsyncSessionLocal() as session:
        user = await UserRepository.get_user_by_tg_id(session, message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return

        referrals = await UserRepository.get_user_referrals(session, user.user_hash)
        if not referrals:
            await message.answer(USER_LEXICON["user_referrals_empty"])
            return

        text = USER_LEXICON["user_referrals_header"]
        
        # Show first 30 referrals
        for referral in referrals[:30]:
            text += USER_LEXICON["user_referrals_item"].format(
                tg_id=referral.tg_id,
                coins=referral.coins,
            )

        if len(referrals) > 30:
            text += USER_LEXICON["user_referrals_more"].format(count=len(referrals) - 30)

        await message.answer(text, parse_mode="Markdown")


@router.message(Command("help"), IsPrivateChat())
async def cmd_help(message: types.Message) -> None:
    """Обработчик команды /help - справка по пользовательским командам.
    
    Выводит полный список доступных пользовательских команд 
    с кратким описанием функциональности каждой.
    
    Параметры:
        message (types.Message): Telegram сообщение с командой /help
    
    Возвращает:
        None: Отправляет справку пользователю"""
    text = USER_LEXICON["user_help"]
    await message.answer(text, parse_mode="Markdown")

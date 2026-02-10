"""Обработчики административных команд бота.

Этот модуль содержит асинхронные обработчики для административных команд,
позволяющих админам просматривать статистику, управлять пользователями и выполнять
различные операции по обслуживанию бота.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db.database import AsyncSessionLocal
from db.requests_db import UserRepository
from filters.filters import AdminFilter
from lexicon.lexicon import ADMIN_LEXICON

router = Router(name="admin_router")


@router.message(Command("admin_stats"), AdminFilter())
async def admin_stats(message: Message) -> None:
    """Обработчик команды /admin_stats - статистика базы данных.
    
    Выводит основную статистику по базе данных:
    - Общее количество пользователей в системе
    - Общее количество монет распределённых в системе
    - Средний баланс монет на одного пользователя
    
    Доступно только администраторам (в списке ADMIN_IDS).
    
    Параметры:
        message (Message): Telegram сообщение с командой /admin_stats
    
    Возвращает:
        None: Отправляет статистику или сообщение об отсутствии пользователей
    """
    async with AsyncSessionLocal() as session:
        users_count = await UserRepository.get_users_count(session)
        
        if users_count == 0:
            await message.answer(ADMIN_LEXICON["admin_stats_empty"])
            return
            
        all_users = await UserRepository.get_all_users(session)
        total_coins = sum(user.coins for user in all_users)
        avg_coins = total_coins / users_count

        text = (
            ADMIN_LEXICON["admin_stats_header"] +
            ADMIN_LEXICON["admin_stats_users"].format(users_count=users_count) +
            ADMIN_LEXICON["admin_stats_total_coins"].format(total_coins=total_coins) +
            ADMIN_LEXICON["admin_stats_avg_coins"].format(avg_coins=avg_coins)
        )
        await message.answer(text, parse_mode="Markdown")


@router.message(Command("admin_users"), AdminFilter())
async def admin_users_list(message: Message) -> None:
    """Обработчик команды /admin_users - список всех пользователей.
    
    Выводит список всех зарегистрированных пользователей с информацией:
    - Порядковый номер
    - Telegram ID
    - Текущий баланс монет
    - Хеш пользователя (первые 12 символов)
    
    Список ограничен 30 пользователями на странице.
    Остаток показывается в виде "и ещё X пользователей".
    
    Доступно только администраторам.
    
    Параметры:
        message (Message): Telegram сообщение с командой /admin_users
    
    Возвращает:
        None: Отправляет список пользователей или уведомление о пустой БД
    """
    async with AsyncSessionLocal() as session:
        users = await UserRepository.get_all_users(session)

        if not users:
            await message.answer(ADMIN_LEXICON["admin_users_empty"])
            return

        text = ADMIN_LEXICON["admin_users_header"].format(count=len(users))
        
        # Show first 30 users
        for i, user in enumerate(users[:30], 1):
            text += ADMIN_LEXICON["admin_users_item"].format(
                i=i,
                tg_id=user.tg_id,
                user_hash=user.user_hash[:12],
                coins=user.coins,
            )

        if len(users) > 30:
            text += ADMIN_LEXICON["admin_users_more"].format(count=len(users) - 30)

        await message.answer(text, parse_mode="Markdown")


@router.message(Command("admin_help"), AdminFilter())
async def admin_help(message: Message) -> None:
    """Обработчик команды /admin_help - справка по административным командам.
    
    Выводит полный список доступных административных команд:
    - /admin_stats: просмотр статистики БД
    - /admin_users: список пользователей
    - /admin_help: эта справка
    
    Доступно только администраторам.
    
    Параметры:
        message (Message): Telegram сообщение с командой /admin_help
    
    Возвращает:
        None: Отправляет справку администратору
    """
    text = (
        ADMIN_LEXICON["admin_help_header"] +
        ADMIN_LEXICON["admin_help_stats"] +
        ADMIN_LEXICON["admin_help_users"] +
        ADMIN_LEXICON["admin_help_add_to_user"] +
        ADMIN_LEXICON["admin_help_add_referral_earnings"] +
        ADMIN_LEXICON["admin_help_add_referral_coins"] +
        ADMIN_LEXICON["admin_help_add_referral_days"] +
        ADMIN_LEXICON["admin_help_set_referral_percentage"] +
        ADMIN_LEXICON["admin_help_help"]
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("add_to_user"), AdminFilter())
async def add_to_user(message: Message) -> None:
    """Обработчик команды /add_to_user - добавить монеты и/или дни подписки пользователю.
    
    Формат команды: /add_to_user <tg_id> <coins> <days>
    Примеры: 
    /add_to_user 123456789 100 0     - добавить 100 монет
    /add_to_user 123456789 0 30      - добавить 30 дней подписки
    /add_to_user 123456789 100 30    - добавить 100 монет и 30 дней
    
    Доступно только администраторам.
    
    Параметры:
        message (Message): Telegram сообщение с командой /add_to_user
    
    Возвращает:
        None: Отправляет результат операции
    """
    try:
        # Parse command arguments
        args = message.text.split()[1:]
        if len(args) != 3:
            await message.answer(ADMIN_LEXICON["add_to_user_usage"])
            return
            
        tg_id = int(args[0])
        coins = int(args[1])
        days = int(args[2])
        
        # Validate that at least one of coins or days is non-zero
        if coins == 0 and days == 0:
            await message.answer(ADMIN_LEXICON["add_to_user_usage"])
            return
        
        async with AsyncSessionLocal() as session:
            # Find user by tg_id
            user = await UserRepository.get_user_by_tg_id(session, tg_id)
            if not user:
                await message.answer(ADMIN_LEXICON["user_not_found"].format(tg_id=tg_id))
                return
                
            # Track what operations were performed
            operations = []
            
            # Add coins to user if specified
            if coins != 0:
                updated_user = await UserRepository.add_coins(session, user.id, coins)
                if updated_user:
                    operations.append(
                        ADMIN_LEXICON["add_coins_success"].format(
                            tg_id=tg_id,
                            amount=coins,
                            new_balance=updated_user.coins
                        )
                    )
                else:
                    operations.append(ADMIN_LEXICON["operation_failed"] + " (монеты)")
            
            # Add days to user subscription if specified
            if days != 0:
                # Refresh user object to get latest data after coins update
                if coins != 0:
                    user = await UserRepository.get_user_by_id(session, user.id)
                
                updated_user = await UserRepository.extend_subscription(session, user.id, days)
                if updated_user:
                    operations.append(
                        ADMIN_LEXICON["add_days_success"].format(
                            tg_id=tg_id,
                            days=days,
                            new_date=updated_user.subscription_until.strftime("%d.%m.%Y %H:%M")
                        )
                    )
                else:
                    operations.append(ADMIN_LEXICON["operation_failed"] + " (подписка)")
            
            # Send combined result
            if operations:
                await message.answer("\n".join(operations))
            else:
                await message.answer(ADMIN_LEXICON["operation_failed"])
    except ValueError:
        await message.answer(ADMIN_LEXICON["add_to_user_usage"])
    except Exception as e:
        await message.answer(ADMIN_LEXICON["operation_failed"] + f"\nОшибка: {str(e)}")


@router.message(Command("add_referral_earnings"), AdminFilter())
async def add_referral_earnings(message: Message) -> None:
    """Обработчик команды /add_referral_earnings - добавить заработок с реферальной системы пользователю.
    
    Формат команды: /add_referral_earnings <tg_id|user_hash> <amount>
    Примеры: 
    /add_referral_earnings 123456789 100
    /add_referral_earnings abc123def456 100
    
    Доступно только администраторам.
    
    Параметры:
        message (Message): Telegram сообщение с командой /add_referral_earnings
    
    Возвращает:
        None: Отправляет результат операции
    """
    try:
        # Parse command arguments
        args = message.text.split()[1:]
        if len(args) != 2:
            await message.answer(ADMIN_LEXICON["add_referral_earnings_usage"])
            return
            
        user_identifier = args[0]
        amount = int(args[1])
        
        async with AsyncSessionLocal() as session:
            # Find user by tg_id or user_hash
            if user_identifier.isdigit():
                # It's a tg_id
                user = await UserRepository.get_user_by_tg_id(session, int(user_identifier))
            else:
                # It's a user_hash
                user = await UserRepository.get_user_by_hash(session, user_identifier)
                
            if not user:
                await message.answer(ADMIN_LEXICON["user_not_found"].format(tg_id=user_identifier))
                return
                
            # Add referral earnings to user
            updated_user = await UserRepository.add_referral_earnings(session, user.id, amount)
            if updated_user:
                await message.answer(
                    ADMIN_LEXICON["add_referral_earnings_success"].format(
                        tg_id=user_identifier,
                        amount=amount,
                        new_earnings=updated_user.referral_earnings
                    )
                )
            else:
                await message.answer(ADMIN_LEXICON["operation_failed"])
    except ValueError:
        await message.answer(ADMIN_LEXICON["add_referral_earnings_usage"])
    except Exception as e:
        await message.answer(ADMIN_LEXICON["operation_failed"] + f"\nОшибка: {str(e)}")


@router.message(Command("set_referral_percentage"), AdminFilter())
async def set_referral_percentage(message: Message) -> None:
    """Обработчик команды /set_referral_percentage - установить процент реферального вознаграждения пользователю.
    
    Формат команды: /set_referral_percentage <tg_id|user_hash> <percentage>
    Примеры:
    /set_referral_percentage 123456789 10
    /set_referral_percentage abc123def456 10
    
    Доступно только администраторам.
    
    Параметры:
        message (Message): Telegram сообщение с командой /set_referral_percentage
    
    Возвращает:
        None: Отправляет результат операции
    """
    try:
        # Parse command arguments
        args = message.text.split()[1:]
        if len(args) != 2:
            await message.answer(ADMIN_LEXICON["set_referral_percentage_usage"])
            return
            
        user_identifier = args[0]
        percentage = int(args[1])
        
        # Validate percentage range (0-100)
        if percentage < 0 or percentage > 100:
            await message.answer("❌ Процент должен быть в диапазоне от 0 до 100")
            return
        
        async with AsyncSessionLocal() as session:
            # Find user by tg_id or user_hash
            if user_identifier.isdigit():
                # It's a tg_id
                user = await UserRepository.get_user_by_tg_id(session, int(user_identifier))
            else:
                # It's a user_hash
                user = await UserRepository.get_user_by_hash(session, user_identifier)
                
            if not user:
                await message.answer(ADMIN_LEXICON["user_not_found"].format(tg_id=user_identifier))
                return
                
            # Store old percentage before updating
            old_percentage = user.referral_percentage
            
            # Update referral percentage for user
            updated_user = await UserRepository.update_referral_percentage(session, user.id, percentage)
            if updated_user:
                await message.answer(
                    ADMIN_LEXICON["set_referral_percentage_success"].format(
                        tg_id=user_identifier,
                        percentage=updated_user.referral_percentage,
                        old_percentage=old_percentage
                    )
                )
            else:
                await message.answer(ADMIN_LEXICON["operation_failed"])
    except ValueError:
        await message.answer(ADMIN_LEXICON["set_referral_percentage_usage"])
    except Exception as e:
        await message.answer(ADMIN_LEXICON["operation_failed"] + f"\nОшибка: {str(e)}")


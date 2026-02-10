# Vocabulary and messages
LEXICON_RU = {
    'yes': '✅ Да',
    'no': '❌ Нет',
    'cancel': 'Отменить',
}

# User handler messages
USER_LEXICON = {
    # Start command
    "user_start": (
        "Добро пожаловать! 👋\n\n"
        "Ваш хеш: `{hash}`\n"
        "Баланс: {coins} 💰\n"
    ),
    
    # Profile
    "user_profile": (
        "👤 **Профиль**\n\n"
        "ID: `{id}`\n"
        "Telegram ID: `{tg_id}`\n"
        "Хеш: `{user_hash}`\n"
        "💰 Баланс: {coins} монет\n"
        "👥 Приглашено: {invited} пользователей\n"
        "💸 Заработок с рефералов: {referral_earnings} монет\n"
    ),
    
    # Referrals
    "user_referrals_header": "🔗 **Мои рефералы**\n\n",
    "user_referrals_item": "👤 ID: `{tg_id}` | Баланс: {coins} 💰\n",
    "user_referrals_empty": "📭 У вас пока нет рефералов",
    "user_referrals_more": "\n... и ещё {count} рефералов",
    
    # Help
    "user_help": (
        "📖 **Справка**\n\n"
        "/start - Главное меню\n"
        "/profile - Профиль\n"
        "/balance - Баланс\n"
        "/referrals - Мои рефералы\n"
        "/help - Эта справка"
    ),
}

# Admin handler messages
ADMIN_LEXICON = {
    # Statistics
    "admin_stats_empty": "📭 Нет пользователей в БД",
    "admin_stats_header": "📊 **Статистика БД**\n\n",
    "admin_stats_users": "👥 Пользователей: {users_count}\n",
    "admin_stats_total_coins": "💰 Всего монет: {total_coins}\n",
    "admin_stats_avg_coins": "📈 Средний баланс: {avg_coins:.1f} 💰\n",
    
    # Users list
    "admin_users_empty": "📭 Нет пользователей",
    "admin_users_header": "👥 **Пользователи** (всего: {count})\n\n",
    "admin_users_item": "{i}. ID: {tg_id} | Хеш: {user_hash} | Баланс: {coins} 💰\n",
    "admin_users_more": "\n... и еще {count} пользователей",
    
    # Help
    "admin_help_header": "🔧 **Администраторские команды**\n\n",
    "admin_help_stats": "/admin_stats - Статистика БД (пользователи, монеты)\n",
    "admin_help_users": "/admin_users - Список всех пользователей\n",
    "admin_help_add_to_user": "/add_to_user <tg_id> <coins> <days> - Добавить монеты и/или дни подписки пользователю\n",
    "admin_help_add_referral_earnings": "/add_referral_earnings <tg_id|user_hash> <amount> - Добавить заработок с реферальной системы пользователю\n",
    "admin_help_add_referral_coins": "/add_referral_coins <user_hash> <ref_index> <amount> - Добавить монеты рефералу\n",
    "admin_help_add_referral_days": "/add_referral_days <user_hash> <ref_index> <days> - Добавить дни подписки рефералу\n",
    "admin_help_set_referral_percentage": "/set_referral_percentage <tg_id|user_hash> <percentage> - Установить процент реферального вознаграждения пользователю\n",
    "admin_help_help": "/admin_help - Эта справка\n",
    
    # Add coins/days messages
    "add_coins_usage": "❌ Неправильный формат команды.\nИспользуйте: /add_coins <tg_id> <amount>",
    "add_days_usage": "❌ Неправильный формат команды.\nИспользуйте: /add_days <tg_id> <days>",
    "add_to_user_usage": "❌ Неправильный формат команды.\nИспользуйте: /add_to_user <tg_id> <coins> <days>\nПримеры:\n/add_to_user 123456789 100 0    - добавить 100 монет\n/add_to_user 123456789 0 30     - добавить 30 дней\n/add_to_user 123456789 100 30   - добавить 100 монет и 30 дней",
    "add_referral_coins_usage": "❌ Неправильный формат команды.\nИспользуйте: /add_referral_coins <user_hash> <ref_index> <amount>",
    "add_referral_days_usage": "❌ Неправильный формат команды.\nИспользуйте: /add_referral_days <user_hash> <ref_index> <days>",
    "add_referral_earnings_usage": "❌ Неправильный формат команды.\nИспользуйте: /add_referral_earnings <tg_id|user_hash> <amount>\nПримеры:\n/add_referral_earnings 123456789 100\n/add_referral_earnings abc123def456 100",
    "set_referral_percentage_usage": "❌ Неправильный формат команды.\nИспользуйте: /set_referral_percentage <tg_id|user_hash> <percentage>\nПримеры:\n/set_referral_percentage 123456789 10\n/set_referral_percentage abc123def456 10",
    "user_not_found": "❌ Пользователь с хешем {tg_id} не найден",
    "no_referrals": "❌ У пользователя с хешем {tg_id} нет рефералов",
    "invalid_referral_index": "❌ Неверный индекс реферала. Доступно рефералов: {count}",
    "operation_failed": "❌ Операция не выполнена",
    "add_coins_success": "✅ Успешно добавлено {amount} монет пользователю {tg_id}\nНовый баланс: {new_balance} 💰",
    "add_days_success": "✅ Успешно добавлено {days} дней подписки пользователю {tg_id}\nНовая дата окончания: {new_date}",
    "add_referral_earnings_success": "✅ Успешно добавлено {amount} к заработку с реферальной системы пользователю {tg_id}\nНовый заработок: {new_earnings} 💰",
    "add_referral_coins_success": "✅ Успешно добавлено {amount} монет рефералу {ref_tg_id}\nНовый баланс: {new_balance} 💰",
    "add_referral_days_success": "✅ Успешно добавлено {days} дней подписки рефералу {ref_tg_id}\nНовая дата окончания: {new_date}",
    "set_referral_percentage_success": "✅ Успешно установлен процент реферального вознаграждения для пользователя {tg_id}\nНовый процент: {percentage}%\nПредыдущий процент: {old_percentage}%",
}

# Bot commands for menu
LEXICON_COMMANDS = {
    '/start': 'Главное меню',
    '/profile': 'Мой профиль',
    '/balance': 'Мой баланс',
    '/referrals': 'Мои рефералы',
    '/help': 'Справка',
}

# Export combined LEXICON
LEXICON = {
    **LEXICON_RU,
    **USER_LEXICON,
    **ADMIN_LEXICON,
}

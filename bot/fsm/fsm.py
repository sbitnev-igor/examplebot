"""Состояния конечного автомата (FSM) для управления диалогом.

Определяет различные стадии диалога пользователя с ботом,
используется для многошаговых операций требующих ввода данных.
"""

from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """Состояния диалога обычных пользователей.
    
    Используется для отслеживания шагов в многошаговых операциях,
    допускающих пользовательский ввод или подтверждение.
    
    Атрибуты:
        waiting_for_input (State): Ожидание ввода от пользователя
    """

    waiting_for_input = State()


class AdminState(StatesGroup):
    """Состояния диалога администраторов.
    
    Используется для управления сложными административными операциями,
    поддерживает многошаговые диалоги для ввода данных.
    
    Атрибуты:
        search_user (State): Поиск пользователя по ID
        add_coins (State): Добавление монет пользователю
        subtract_coins (State): Вычитание монет у пользователя
        extend_sub (State): Продление подписки пользователю
        broadcast_content (State): Получение контента для рассылки
        broadcast_button (State): Получение информации о кнопке для рассылки
    """

    search_user = State()
    add_coins = State()
    subtract_coins = State()
    extend_sub = State()
    broadcast_content = State()
    broadcast_button = State()

from typing import Union
from telebot import types


class general:
    def role_keyboard() -> types: 
        """возвращает готовую клавиатуру для выбора роли"""

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True , one_time_keyboard=True)
        markup.add("📢 Заказчик" , "🧑‍💻 Исполнитель" , "🏢сотрудник")

        return markup
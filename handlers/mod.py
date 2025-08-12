from telebot import types
from telebot import TeleBot
import logging
import data_base as db
import keyboards
from config import chat_mod

logger = logging.getLogger(__name__)

def register_mod(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('aproved_topup_' , 'disaproved_topup_')))
    def approv_topup(call):
        do , _ , empluyer_id , amount = call.data.split('_')
        
        if do == 'aproved':
            db.updata.topup(empluyer_id , amount)
            bot.send_message(empluyer_id , f'ваш баланс пополнен')
            markup = types.InlineKeyboardMarkup()
            bot.edit_message_text('Заявка обработана' , chat_mod , call.message.message_id , reply_markup=markup)
            logger.info(f'aproved top up for {empluyer_id}')
            
        else:
            bot.send_message(empluyer_id , f'Была допущена ошибка при пополнение, обратитесь в техническую поддержку')
            logger.info(f'disaproved top up for {empluyer_id}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('approved_withdraw_', 'disapproved_withdraw_')))
    def approve_withdraw(call):
        action, _, user_id, amount = call.data.split('_')
        user_id = int(user_id)
        amount = float(amount)

        if action == 'approved':
            db.updata.withdraw(user_id, amount)  # Убедись, что такая функция есть и уменьшает баланс
            bot.send_message(user_id, f"✅ Ваш запрос на вывод {amount} ₽ был одобрен. Средства скоро поступят.")
            logger.info(f'approved withdraw for {user_id}')

            # Убираем кнопки
            bot.edit_message_text("Заявка на вывод обработана ✅", chat_mod, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())

        else:
            bot.send_message(user_id, f"❌ Ваш запрос на вывод средств был отклонён. Обратитесь в поддержку при необходимости.")
            logger.info(f'disapproved withdraw for {user_id}')

            bot.edit_message_text("Заявка на вывод отклонена ❌", chat_mod, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())



    @bot.callback_query_handler(func=lambda call: call.data.startswith(('support_progress_', 'support_resolve_')))
    def handle_support_status(call):
        _ , action , ticket_id = call.data.split('_')
        user_id = int(ticket_id.split("-")[0])

        if action == 'progress':
            markup = types.InlineKeyboardMarkup()
            resolve_btn = types.InlineKeyboardButton("✅ Закрыть", callback_data=f"support_resolve_{ticket_id}")
            markup.add(resolve_btn)
            logger.info(f'beginning of the review: {ticket_id}')

            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id , reply_markup=markup)
            
        elif action == 'resolve':
            bot.edit_message_text("✅ Заявка закрыта", call.message.chat.id, call.message.message_id)
            bot.send_message(user_id , 'Ваша заявка в техническую поддрежку была решина')
            logger.info(f'application is closed: {ticket_id}')

from telebot import types
from datetime import datetime
from telebot import TeleBot
import logging
import data_base as db
from decorations import *
import support
import keyboards
from config import chat_mod

logger = logging.getLogger(__name__)

def student_home_page(bot: TeleBot , user_id: int):
    """Отображает домашнюю страницу исполнителя"""

    student_data = db.get.student_data(user_id)
    rating = student_data['rating_sum']/student_data['rating_number']
    
    if int(rating) == rating:
        rating = int(rating)
        
    else:
        rating = round(rating, 2)
    
    
    message = str(
        f"<b>🎓 {student_data['name']}</b>\n\n"
        f"⭐ <b>Твой рейтинг:</b> {rating}/5\n"
        f"📂 <b>Выполнено работ:</b> {student_data['rating_number']-1}\n"
        f"💰 <b>Баланс:</b> {student_data['balance']} ₽\n\n"
        f"Находи подработки, откликайся и зарабатывай!"
)
    
    bot.send_message(user_id , message , reply_markup=keyboards.student.home() , parse_mode='HTML')

def register_student(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "🔍 Поиск вакансий")
    @student_only(bot , lambda msg: msg)
    def start_search_jobs(msg):
        try:
            all_jobs = db.get.job_ids()
            if all_jobs:
                support.student.show_job(bot , msg.from_user.id , all_jobs[0] , 0 , msg.message_id)
            
            else:
                bot.send_message(msg.chat.id , 'Пока нет доступных вакансий')
            
        except Exception as e:
            logger.error(f'Error in start_search_jobs: {e}')

    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('student_project_prev_' , 'student_project_boundary_first' , 'student_project_next_' , 'student_project_boundary_last')))
    @student_only(bot , lambda msg: msg)
    def navigation_student_job(call):
        try:
            if call.data.startswith(('student_project_prev_' , 'student_project_next_')):
                _ , _ , _ , job_id , index = call.data.split('_')
                job_id , index = int(job_id) , int(index)
                
                all_job = db.get.job_ids()
                if not all_job:
                    bot.answer_callback_query(call.id , 'Нет доступных проектов')
                    return
                
                new_job_id = all_job[index]
                
                support.student.show_job(
                    bot , 
                    call.message.chat.id , 
                    new_job_id , 
                    index , 
                    call.message.message_id
                )
                
            else:
                if call.data == 'student_project_boundary_first':
                    bot.answer_callback_query(call.id, "Это крайная работа", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайная работа", show_alert=True)
        
        except Exception as e:
            logger.error(f'Error in navigation_student_job: {e}')
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('apply_job_'))
    @student_only(bot , lambda msg: msg)
    def apply_job_student(call):
        try:
            job_id = int(call.data.split('_')[2])
            result = db.add.application(job_id , call.message.chat.id)
            student_name = db.get.user_info(call.message.chat.id , 'name')
            job = db.get.job_details(job_id)

            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            message = str(
                f'====== отклик на вакансию ======\n'
                f'Исполнитель: {student_name}\n'
                f'Вакансия: {job['title']}\n'
                f'Время отклика: {now}\n'
                '================================='
            )
            
            bot.send_message(job['staff'] , message)
            bot.answer_callback_query(call.id , result , show_alert=True)
            
            if result:
                logger.info(f'New application to {job_id} from {call.message.chat.id}')
            
            
        except Exception as e:
            logger.error(f'Error in apply_job_student: {e}')

    
    
    @bot.message_handler(func=lambda msg: msg.text == '📄 Мои работы')
    @student_only(bot , lambda msg: msg)
    def my_job_student(msg):
        try:
            studdent_id = msg.from_user.id
            app_ids = db.get.applications_student(msg.chat.id)
            
            
            if app_ids:
                support.student.my_job(bot , msg.chat.id , app_ids[0] , 0 , msg.message_id)
                
            else:
                bot.send_message(msg.chat.id , 'У вас пока нет работ')
        
        except Exception as e:
            logger.error(f'Error in my_job_student: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('student_myjob_prev_' , 'student_myjob_boundary_first' , 'student_myjob_next_' , 'student_myjob_boundary_last')))
    @student_only(bot , lambda msg: msg)
    def navigation_stydent_job(call):
        try:
            if call.data.startswith(('student_myjob_prev_' , 'student_myjob_next_')):
                _ , _ , _ , job_id , index = call.data.split('_')
                index = int(index)
                student_id = call.message.chat.id
                app_ids = db.get.applications_student(call.message.chat.id)
                
                if not app_ids:
                    bot.answer_callback_query(call.id , 'У вас нет проектов')
                    return
                
                new_job_id = app_ids[index]
                
                support.student.my_job(
                    bot , 
                    student_id , 
                    new_job_id , 
                    index , 
                    call.message.message_id
                )
                
            else:
                if call.data == 'student_myjob_boundary_last':
                    bot.answer_callback_query(call.id, "Это крайний работа", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайний работа", show_alert=True)
                    
        except Exception as e:
            logger.error(f'Error in navigation_stydent_job: {e}')
            
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
    @student_only(bot , lambda msg: msg)
    def start_stydent_job(call):
        try:
            _ , app_id , index= call.data.split('_')
            time = datetime.now().strftime("%H:%M")
            job_id = db.updata.start_jobs(app_id , time)
            
            if job_id:
                app = db.get.application_details(app_id)
                job_title = db.get.job_info(job_id , 'title')
                employer_id = db.get.job_info(job_id , 'staff')
                student_name = db.get.user_info(app['user_id'] , 'name')
                
                bot.send_message(employer_id , 
                    f'====== начала работы ======\n'
                    f'исполнитель: {student_name}\n'
                    f'Задача: {job_title}\n'
                    f'Время: {time}\n'
                    '============================')
                bot.answer_callback_query(call.id , 'Вы начали работу' , show_alert=True)
                
                support.student.my_job(
                    bot , 
                    call.message.chat.id , 
                    app_id , 
                    int(index) , 
                    call.message.message_id
                )
                logger.info(f'student: {call.message.chat.id} start job: {job_id}')
        
        except Exception as e:
            logger.error(f'Error in start_stydent_job: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('finish_'))
    @student_only(bot , lambda msg: msg)
    def finish_stydent_job(call):
        try:
            _ , app_id , index= call.data.split('_')
            time = datetime.now().strftime("%H:%M")
            job_id = db.updata.finish_jobs(app_id , time)
            
            if job_id:
                app = db.get.application_details(app_id)
                job_title = db.get.job_info(job_id , 'title')
                employer_id = db.get.job_info(job_id , 'staff')
                student_name = db.get.user_info(app['user_id'] , 'name')
                
                bot.send_message(employer_id , 
                    f'====== завершение работы ======\n'
                    f'исполнитель: {student_name}\n'
                    f'Задача: {job_title}\n'
                    f'Время: {time}\n'
                    '================================')
                bot.answer_callback_query(call.id , 'Вы начали работу' , show_alert=True)
                
                support.student.my_job(
                    bot , 
                    call.message.chat.id , 
                    app_id , 
                    int(index) , 
                    call.message.message_id
                )
                logger.info(f'student: {call.message.chat.id} finish job: {job_id}')
        
        except Exception as e:
            logger.error(f'Error in finish_stydent_job: {e}')
            
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith('comleted_'))
    @student_only(bot , lambda msg: msg)
    def job_comleted1(call):
        try:
            _ , index , app_id , student_id = call.data.split('_')
            index , app_id , student_id = map(int , [index , app_id , student_id])
            markup = types.InlineKeyboardMarkup()
            all_app = db.get.applications_student(student_id)
            job_id = db.get.application_info(app_id , 'job_id')
            
            btns = keyboards.student.finished(index , all_app , job_id)
            for i in btns:
                markup.row(i)
            
            bot.send_message(student_id , 'оцените заказчика' , reply_markup=markup)
            
        
        except Exception as e:
            logger.error(f'Error in job_comleted1: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('comlet_'))
    @student_only(bot , lambda msg: msg)
    def application_confirm1(call):
        try:
            _ , app_id , index , job_id , score = call.data.split('_')
            index , app_id , score = int(index) , int(app_id) , int(score)
            employer_id = db.get.job_info(app_id , 'employer_id')
            
            result1 = db.updata.user_rating(employer_id , score)
            result2 = db.updata.application_confirm(app_id)
            
            if result1 and result2:
                bot.edit_message_text('оценка оставлена' , call.message.chat.id , call.message.message_id)
                
        except Exception as e:
            logger.error(f'Error in apllication_confirm1: {e}' , exc_info=True)
            

    @bot.message_handler(func=lambda m: m.text == "💸 Вывести средства")
    @student_only(bot, lambda msg: msg)
    def start_withdraw(msg):
        bot.send_message(msg.chat.id, 'Введите сумму, которую хотите вывести.')
        bot.register_next_step_handler(msg, get_withdraw_amount)


    def get_withdraw_amount(msg):
        try:
            amount = float(msg.text)
            user_id = msg.from_user.id
            balance = db.get.user_info(user_id, 'balance')

            if amount <= 0:
                raise ValueError

            if balance < amount:
                bot.send_message(msg.chat.id, "Недостаточно средств на балансе.")
                return

            bot.set_state(user_id, 'process_withdraw', msg.chat.id)
            bot.add_data(user_id, msg.chat.id, withdraw_amount=amount)

            bot.send_message(
                msg.chat.id,
                "Введите реквизиты для перевода (номер карты, счёт и т.п.):"
            )
            bot.register_next_step_handler(msg, get_withdraw_details)

        except ValueError:
            bot.send_message(msg.chat.id, "Пожалуйста, введите корректную сумму.")
            bot.register_next_step_handler(msg, get_withdraw_amount)


    def get_withdraw_details(msg):
        user_id = msg.from_user.id
        payment_details = msg.text

        with bot.retrieve_data(user_id, msg.chat.id) as data:
            amount = data['withdraw_amount']

        name = db.get.user_info(user_id, 'name')
        username = db.get.user_info(user_id, 'user_name')

        caption = (
            f"📤 Заявка на вывод средств\n"
            f"👤 Пользователь: {name} (@{username})\n"
            f"🆔 ID: {user_id}\n"
            f"💸 Сумма: {amount} ₽\n"
            f"📎 Реквизиты: {payment_details}\n"
        )

        markup = types.InlineKeyboardMarkup()
        approve_btn = types.InlineKeyboardButton('✅ подтвердить', callback_data=f'approved_withdraw_{msg.chat.id}_{amount}')
        disapprove_btn = types.InlineKeyboardButton('❌ отклонить', callback_data=f'disapproved_withdraw_{msg.chat.id}_{amount}')
        markup.row(approve_btn, disapprove_btn)

        bot.send_message(chat_mod, caption, reply_markup=markup)
        bot.send_message(msg.chat.id, "Заявка на вывод отправлена модераторам. Ожидайте подтверждения.")
        logger.info(f'request for withdraw from: {msg.chat.id}')



    @bot.message_handler(func=lambda m: m.text == "🛠 Техподдержка")
    def start_support(msg):
        bot.send_message(msg.chat.id, "✏️ Пожалуйста, опишите вашу проблему одним сообщением.")
        bot.register_next_step_handler(msg, handle_support_request)


    def handle_support_request(msg):
        user_id = msg.from_user.id
        name = db.get.user_info(user_id, 'name')
        username = db.get.user_info(user_id, 'user_name')
        text = msg.text

        # ID заявки можно формировать по текущему времени
        ticket_id = f"{user_id}-{int(datetime.now().timestamp())}"


        # Уведомление модераторам
        message = (
            f"🆘 *Новая заявка в техподдержку*\n"
            f"🆔 Ticket ID: `{ticket_id}`\n"
            f"👤 Пользователь: {name} (@{username})\n"
            f"📩 Сообщение: {text}\n"
        )

        markup = types.InlineKeyboardMarkup()
        in_progress_btn = types.InlineKeyboardButton("🛠 В работу", callback_data=f"support_progress_{ticket_id}")
        markup.add(in_progress_btn)

        bot.send_message(chat_id=chat_mod, text=message , reply_markup=markup)

        bot.send_message(msg.chat.id, "📨 Ваша заявка отправлена. Ожидайте ответа от модератора.")
        logger.info(f'request for request from: {msg.chat.id}')
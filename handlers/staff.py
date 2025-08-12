from telebot import types
from telebot import TeleBot
from datetime import datetime
import logging
import data_base as db
import keyboards
import support
from decorations import staff_only
from config import chat_mod

logger = logging.getLogger(__name__)

def staff_home_page(bot: TeleBot , user_id: int):
    """Отображает домашнюю страницу сотрудника"""

    secret_code = db.get.staff_secret_code(user_id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    if secret_code == None:
        name = db.get.user_info(user_id, 'name')
        message = f'Здравствуйте, {name}, для того, чтобы начать работу введите код для присоединении к компании'
        btn = '✍️Ввести код компании'
        markup.add(btn)
        bot.send_message(user_id , message , reply_markup=markup)
    
    else:
        staff = db.get.staff_data(user_id)
        rating = staff['rating']
        if int(rating) == rating:
            rating = int(rating)
        message = str(
            f"<b>👤 {staff['staff_name']}</b>\n\n"
            f"🏢 <b>Компания:</b> {staff['company_name']}\n"
            f"⭐ <b>Рейтинг компании:</b> {rating}/5\n"
            f"📄 <b>Актуальных вакансий:</b> {staff['jobs_count']}\n"
        )
        
        bot.send_message(user_id , message , parse_mode='HTML' , reply_markup=keyboards.staff.staff_home())

def register_staff(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "✍️Ввести код компании")
    @staff_only(bot , lambda msg: msg)
    def start_join_employer(msg):
        try:
            bot.send_message(msg.chat.id, 'Введите код компании: ')
            bot.register_next_step_handler(msg, join_employer)
            
        except Exception as e:
            logger.error(f'Error in start_search_jobs: {e}')
    
    def join_employer(msg):
        employer_id = db.updata.join_employer(msg.chat.id , msg.text)
        logger.info(f'new application for joining the {employer_id}')
        name = db.get.user_info(msg.chat.id, 'name')
        
        bot.send_message(employer_id, f'заявка на присоединение к компании пользователя {name}')
        bot.send_message(msg.chat.id , 'заявка на присоединение отправлина')
    
    
    @bot.message_handler(func=lambda m: m.text == "📂 Мои вакансии")
    @staff_only(bot , lambda msg: msg)
    def staff_jobs(msg):
        try:
            staff_id = int(msg.from_user.id)
            job_ids = db.get.staff_job(staff_id)
            
            if not job_ids:
                bot.send_message(staff_id , "📭 У вас пока нет вакансий.")
                return
            
            support.staff.show_job(bot , msg.chat.id , job_ids[0] , 0 , msg.message_id)
            
        except Exception as e:
            logger.error(f'Error in staff_jobs: {e}')
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('staff_project_prev_' , 'staff_project_next_')) or call.data in (('staff_project_boundary_first', 'staff_project_boundary_last')))
    @staff_only(bot , lambda msg: msg)
    def navigation_staff_job(call):
        try:
            if call.data.startswith(('staff_project_prev_' , 'staff_project_next_')):
                _ , _ , _ , job_id , index = call.data.split('_')
                staff_id = call.message.chat.id
                all_job = db.get.staff_job(staff_id)
                
                if not all_job:
                    bot.answer_callback_query(call.id , 'У вас нет проектов')
                
                new_job_id = all_job[int(index)]
                
                support.staff.show_job(
                    bot , 
                    staff_id , 
                    new_job_id , 
                    index , 
                    call.message.message_id
                )
                
            else:
                if call.data == 'staff_project_boundary_first':
                    bot.answer_callback_query(call.id, "Это крайний вакансия", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайний вакансия", show_alert=True)
        except Exception as e:
            logger.error(f'Error in navigation_staff_job: {e}')


    @bot.callback_query_handler(func=lambda call: call.data.startswith('staffcandidates_'))
    @staff_only(bot , lambda msg: msg)
    def candidates_staff_job(call):
        try:
            _ , job_id = call.data.split('_')
            
            app_ids = db.get.application_by_job(job_id)
            
            if not app_ids:
                bot.answer_callback_query(call.id , "Пока нет откликов на эту вакансию" , show_alert=True)
                return
            
            support.staff.show_aplication(bot , call.message.chat.id , job_id , app_ids[0] , 0 , call.message.message_id)
            
        except Exception as e:
            logger.error(f'Error in cadidstes_staff_job: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('staff_application_prev_' , 'staff_application_boundary_first' , 'staff_applocation_next_' , 'staff_application_boundary_last')))
    @staff_only(bot , lambda msg: msg)
    def navigation_application(call):
        try:
            if call.data.startswith(('staff_application_prev_' , 'staff_applocation_next_')):
                _ , _ , _ , app_id , index , job_id= call.data.split(_)
                staff_id = call.message.chat.id
                all_app = db.get.application_by_job()
                
                if not all_app:
                    bot.answer_callback_query(call.id , 'У вас нет проектов')
                    return
                
                new_job_id = all_app[index]
                
                support.staff.show_job(
                    bot , 
                    staff_id , 
                    new_job_id , 
                    index , 
                    call.message.message_id
                )
                
            else:
                if call.data == 'staff_application_boundary_first':
                    bot.answer_callback_query(call.id, "Это крайний отклик", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайний отклик", show_alert=True)
        except Exception as e:
            logger.error(f'Error in navigation_application: {e}')
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('staff_applocation_approv_'))
    @staff_only(bot , lambda msg: msg)
    def application_approv(call):
        try:
            app_id = call.data.split("_")[3]
            result = db.updata.approv_application(app_id)
            
            if result:
                bot.answer_callback_query(call.id , "Отклик принять" , show_alert=True)
                
                app = db.get.application_details(app_id)
                job = db.get.job_details(app['job_id'])
                
                now = datetime.now().strftime("%d.%m.%Y %H:%M")
                message = str(
                    f'====== отклик принят ======\n'
                    f'Вакансия: {job['title']}\n'
                    f'Компания: {job['employer_name']}\n'
                    f'Время: {now}\n'
                    '============================'
                )
                bot.send_message(app['user_id'] , message)
                
                logger.info(f'application approved: {app_id}')
        
        except Exception as e:
            logger.error(f'Error in application_approv: {e}')

    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('staff_applocation_disapprov_'))
    @staff_only(bot , lambda msg: msg)
    def application_disapprov(call):
        try:
            app_id = call.data.split("_")[3]
            result = db.updata.disapprov_application(app_id)
            
            if result:
                bot.answer_callback_query(call.id , "Отклик откланён" , show_alert=True)
                
                app = db.get.application_details(app_id)
                job = db.get.job_details(app['job_id'])
                
                now = datetime.now().strftime("%d.%m.%Y %H:%M")
                message = str(
                    f'====== отклик отклонён ======\n'
                    f'Вакансия: {job['title']}\n'
                    f'Компания: {job['employer_name']}\n'
                    f'Время: {now}\n'
                    '============================'
                )
                bot.send_message(app['user_id'] , message)
                
                logger.info(f'application approved: {app_id}')
        
        except Exception as e:
            logger.error(f'Error in application_approv: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('staffconfirm_'))
    @staff_only(bot , lambda msg: msg)
    def application_confirm(call):
        try:
            staff_id = int(call.message.chat.id)
            app_ids = db.get.app_ids_finish(int(call.data.split('_')[1]))
            
            if not app_ids:
                bot.send_message(staff_id , 'обратитесь в техническую поддержку')
                return
            
            support.staff.show_finished(bot , staff_id , int(call.data.split('_')[1]) , app_ids , 0 , call.message.message_id)
        
        except Exception as e:
            logger.error(f'Error in application_confirm: {e}' , exc_info=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('stafffinished_'))
    @staff_only(bot , lambda msg: msg)
    def application_confirm1(call):
        try:
            _ , app_id , index , job_id , score = call.data.split('_')
            index , app_id , score = int(index) , int(app_id) , int(score)
            student_id = db.get.application_info(app_id , 'student_id')
            app_ids = db.get.app_ids_finish(job_id)
            
            result1 = db.updata.user_rating(student_id , score)
            result2 = db.updata.job_confirm(app_id , (index+1 == len(app_ids)))
            
            if result1 and result2:
                bot.answer_callback_query(call.id , 'Оценка осавлена')
                
                support.staff.show_finished(bot , int(call.message.chat.id) , job_id , app_ids , index+1 , call.message.message_id)
                
        except Exception as e:
            logger.error(f'Error in apllication_confirm1: {e}' , exc_info=True)
    
    
    
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

        bot.send_message(chat_id=chat_mod, text=message, parse_mode="Markdown", reply_markup=markup)

        bot.send_message(msg.chat.id, "📨 Ваша заявка отправлена. Ожидайте ответа от модератора.")
        logger.info(f'request for request from: {msg.chat.id}')
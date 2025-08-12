from telebot import types
from telebot import TeleBot
from datetime import datetime , timedelta
import logging
import data_base as db
from decorations import *
import support
import keyboards
import keyboards.employer
from config import chat_mod , commission_rate

logger = logging.getLogger(__name__)

def emplouer_home_page(bot: TeleBot , user_id: int):
    """Отображает домашнюю страницу заказчика"""

    employer_data = db.get.employer_data(user_id)

    rating = employer_data['rating_sum']/employer_data['rating_number']
    
    if int(rating) == rating:
        rating = int(rating)
        
    else:
        rating = round(rating, 2)

    message = str(
        f"<b>🏢 {employer_data['name']}</b>\n\n"
        f"⭐ <b>Рейтинг:</b> {rating}/5\n"
        f"👥 <b>Сотрудников:</b> {employer_data['staff_count']}\n"
        f"📄 <b>Актуальных вакансий:</b> {employer_data['jobs_count']}\n"
        f"💰 <b>Баланс:</b> {employer_data['balance']} ₽\n"
        f"🔑 <b>Код для подключения сотрудников:</b> <code>{employer_data['secret_code']}</code>\n\n"
        "Создавайте вакансии, пополняйте баланс и развивайте вашу команду!"
    )
    
    bot.send_message(user_id , message , reply_markup=keyboards.employer.home() , parse_mode='HTML')

def register_employer(bot: TeleBot):
    
    
    @bot.message_handler(func=lambda m: m.text == "➕ Создать вакансию")
    @employer_only(bot , lambda msg: msg)
    def start_create_job(msg):
        try:
            balance = db.get.user_info(msg.chat.id , 'balance')
            
            if balance < 0:
                bot.send_message(msg.chat.id , 'Для создания вакансии погасите задолжность')
            
            else:
                bot.delete_state(msg.chat.id , msg.chat.id)
                bot.set_state(msg.from_user.id , 'process_create' , msg.chat.id)
                
                message = str(
                    "<b>📌 Шаг 1 из 7</b>\n"
                    "Введите <b>название вакансии</b>, которое кратко описывает задачу.\n"
                    "Пример: <i>Раздатчик листовок</i>\n\n"
                    "Для отмены /cancel"
                )
                
                bot.send_message(
                    msg.chat.id ,
                    message , 
                    parse_mode= 'HTML' , 
                    reply_markup=types.ReplyKeyboardRemove()
                )
                
                bot.register_next_step_handler(msg , process_title)

        except Exception as e:
            logger.error(f'Error in start_create_job: {e}')


    def process_title(msg):
        try:
            if msg.text == '/cancel':
                emplouer_home_page(bot , msg.from_user.id)
            
            else:
                bot.add_data(msg.from_user.id , msg.chat.id , title = msg.text)
                
                message = str(
                     "<b>📌 Шаг 2 из 7</b>\n"
                    "Введите <b>подробное описание</b> вакансии.\n"
                    "Что именно нужно будет делать, требования, пожелания.\n"
                    "Не забудьте указать в этом пункте адрес куда надо прийти для начала работы\n\n"
                    "Для отмены /cancel"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML'
                )
                
                bot.register_next_step_handler(msg ,  process_description)
        
        except Exception as e:
            logger.error(f'Error in process_title: {e}')
                
    
    def process_description(msg):
        try:
            if msg.text == '/cancel':
                emplouer_home_page(bot , msg.from_user.id)
                
            else:
                bot.add_data(msg.from_user.id , msg.chat.id , description = msg.text)
            
                message = str(
                    "<b>📌 Шаг 3 из 7</b>\n"
                    "Введите <b>дату выполнения</b> в формате <code>ДД.ММ.ГГГГ</code>.\n"
                    "Пример: <code>15.06.2025</code>\n\n"
                    "Для отмены /cancel"
                )
                
                bot.send_message(
                        msg.chat.id , 
                        message , 
                        parse_mode='HTML'
                )
                
                bot.register_next_step_handler(msg , process_date)
        
        except Exception as e:
            logger.error(f'Error in process_description: {e}')
    
    
    def process_date(msg):
        try:
            if msg.text == '/cancel':
                emplouer_home_page(bot , msg.from_user.id)
                
            else:
                date = datetime.strptime(msg.text, "%d.%m.%Y").date()
                
                if date < (datetime.now().date() + timedelta(days=1)):
                    bot.send_message(
                        msg.chat.id , 
                        'указаная дата меньше чем через неделю' 
                    )
                    return bot.register_next_step_handler(msg , process_date)
                
                bot.add_data(msg.from_user.id , msg.chat.id , date = msg.text)

                message = str(
                    "<b>📌 Шаг 4 из 7</b>\n"
                    "Введите <b>время начала и окончания</b> через дефис.\n"
                    "Формат: <code>ЧЧ:ММ–ЧЧ:ММ</code>\n"
                    "Пример: <code>10:00–16:00</code>\n\n"
                    "Для отмены /cancel"
                )

                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML'
                )
                
                bot.register_next_step_handler(msg , process_time)
        
        except Exception as e:
            logger.error(f'Error in process_date: {e}')
    
    def process_time(msg):
        try:
            if msg.text == '/cancel':
                emplouer_home_page(bot, msg.from_user.id)
            else:
                # Заменяем все типы тире на обычный дефис
                cleaned_text = msg.text.replace('–', '-').replace('—', '-').strip()

                time_parts = cleaned_text.split('-')

                if len(time_parts) != 2:
                    bot.send_message(
                        msg.chat.id,
                        "❌ Неверный формат. Используйте формат: <code>10:00-16:00</code>",
                        parse_mode='HTML'
                    )
                    bot.register_next_step_handler(msg, process_time)
                    return

                time_start = time_parts[0].strip()
                time_end = time_parts[1].strip()

                bot.add_data(msg.from_user.id, msg.chat.id, time_start=time_start)
                bot.add_data(msg.from_user.id, msg.chat.id, time_end=time_end)
                
                message = str(
                    "<b>📌 Шаг 5 из 7</b>\n"
                    "укажите <b>количество исполнителей</b> которые требуются на эту должность\n\n"
                    "Для отмены /cancel"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML'
                )
                
                bot.register_next_step_handler(msg , process_people)
        
        except Exception as e:
            logger.error(f'Error in process_time: {e}')
    
    
    def process_people(msg):
        try:
            if msg.text == '/cancel':
                emplouer_home_page(bot , msg.from_user.id)
                
            else:
                try:
                    people = int(msg.text)
                    bot.add_data(msg.from_user.id , msg.chat.id , people = people)
                    
                    message = str(
                        "<b>📌 Шаг 6 из 7</b>\n"
                        "Введите <b>сумму оплаты</b> за одного исполнителя в рублях.\n"
                        "Пример: <code>1200</code>\n\n"
                        "Для отмены /cancel"
                    )
                    
                    bot.send_message(
                        msg.chat.id , 
                        message , 
                        parse_mode='HTML'
                    )
                    
                    bot.register_next_step_handler(msg , process_price)
                except:
                    bot.send_message(msg.chat.id , 'Укажите цельное число без лишник симвалов')
                    bot.register_next_step_handler(msg , process_people)

        except Exception as e:
            logger.error(f'Error in process_people: {e}')
    
    
    def process_price(msg):
        try:
            if msg.text == '/cancel':
                emplouer_home_page(bot , msg.from_user.id)
                
            else:
                try:
                    price = float(msg.text)
                    bot.add_data(msg.from_user.id , msg.chat.id , price = price)
                    
                    secret_code = db.get.user_info(msg.chat.id , 'secret_code')
                    message = str(
                        "<b>📌 Шаг 7 из 7</b>\n"
                        "Кто будет <b>отвечать за эту вакансию</b>?\n"
                        "Выберите из списка ниже или введите ID сотрудника, если необходимо.\n\n"
                        "Для отмены /cancel"
                    )
                    
                    bot.send_message(
                        msg.chat.id , 
                        message , 
                        reply_markup=keyboards.employer.staff(secret_code) , 
                        parse_mode='HTML'
                    )
                    
                    bot.register_next_step_handler(msg , process_staff)
                
                except:
                    bot.send_message(msg.chat.id , 'Укажите число без лишних симвалов, если хотите указать копейки пишите их через точку')
        
        except Exception as e:
            logger.error(f'Error in process_price: {e}')
    
    
    def process_staff(msg):
        try:
            if msg.text == '/cancel':
                emplouer_home_page(bot , msg.from_user.id)
                
            else:
                with bot.retrieve_data(msg.from_user.id , msg.chat.id) as data:
                    message = str(
                        "<b>✅ Вакансия успешно создана!</b>\n\n"
                        f"📌 <b>Название:</b> {data['title']}\n"
                        f"📝 <b>Описание:</b> {data['description']}\n"
                        f"📅 <b>Дата:</b> {data['date']}\n"
                        f"⏰ <b>Время:</b> {data['time_start']}–{data['time_end']}\n"
                        f"💰 <b>Оплата:</b> {data['price']} ₽\n"
                        f"👤 <b>Ответственный:</b> {msg.text}\n\n"
                        "Теперь вы можете отслеживать статус этой вакансии в разделе <i>«Мои вакансии»</i>."
                    )
                    
                    bot.send_message(
                        msg.chat.id , 
                        message , 
                        reply_markup=types.ReplyKeyboardRemove() , 
                        parse_mode='HTML'
                    )

                    secret_code = db.get.user_info(msg.chat.id , 'secret_code')
                    staff_list = db.get.staff(secret_code)
                    selected_name = msg.text
                    selected_staff = next((s for s in staff_list if s['name'] == selected_name), None)
                    id_staff = selected_staff['user_id']
                    db.add.job(
                        msg.chat.id , 
                        data['title'] ,
                        data['description'] , 
                        data['time_start'] , 
                        data['time_end'] ,
                        data['date'] , 
                        data['price'] ,
                        data['people'] , 
                        id_staff
                    )
        
        except Exception as e:
            logger.error(f'Error in process_price: {e}')
    
    
    
    @bot.message_handler(func=lambda m: m.text == "📋 Мои вакансии")
    @employer_only(bot , lambda msg: msg)
    def my_job_employer(msg):
        try:
            employer_id = int(msg.from_user.id)
            project_ids = db.get.job_ids_employer(employer_id)
            
            if not project_ids:
                bot.send_message(employer_id , "📭 У вас пока нет вакансий.")
                return
            
            support.employer.show_job(bot , msg.chat.id , project_ids[0] , 0 , msg.message_id)
            
        except Exception as e:
            logger.error(f'Error in my_job_employer: {e}')
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('employer_project_prev_' , 'employer_project_next_')) or call.data in (('employer_project_boundary_first', 'employer_project_boundary_last')))
    @employer_only(bot , lambda msg: msg)
    def navigation_employer_job(call):
        try:
            if call.data.startswith(('employer_project_prev_' , 'employer_project_next_')):
                _ , _ , _ , job_id , index = call.data.split('_')
                employer_id = call.message.chat.id
                all_job = db.get.job_ids_employer(employer_id)
                
                if not all_job:
                    bot.answer_callback_query(call.id , 'У вас нет вакансий')
                
                new_job_id = all_job[int(index)]
                
                support.employer.show_job(
                    bot , 
                    employer_id , 
                    new_job_id , 
                    index , 
                    call.message.message_id
                )
                
            else:
                if call.data == 'employer_project_boundary_first':
                    bot.answer_callback_query(call.id, "Это крайний вакансия", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайний вакансия", show_alert=True)
        except Exception as e:
            logger.error(f'Error in navigation_employer_job: {e}')


    @bot.callback_query_handler(func=lambda call: call.data.startswith('candidates_'))
    @employer_only(bot , lambda msg: msg)
    def candidates_employer_job(call):
        try:
            _ , job_id = call.data.split('_')
            
            app_ids = db.get.application_by_job(job_id)
            
            if not app_ids:
                bot.answer_callback_query(call.id , "Пока нет откликов на эту вакансию" , show_alert=True)
                return
            
            support.employer.show_aplication(bot , call.message.chat.id , job_id , app_ids[0] , 0 , call.message.message_id)
            
        except Exception as e:
            logger.error(f'Error in cadidstes_employer_job: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('employer_application_prev_' , 'employer_application_boundary_first' , 'employer_applocation_next_' , 'employer_application_boundary_last')))
    @employer_only(bot , lambda msg: msg)
    def navigation_application(call):
        try:
            if call.data.startswith(('employer_application_prev_' , 'employer_applocation_next_')):
                _ , _ , _ , app_id , index , job_id= call.data.split('_')
                index , job_id , app_id = int(index) , int(job_id) , int(app_id)
                employer_id = call.message.chat.id
                all_app = db.get.application_by_job(job_id)
                
                if not all_app:
                    bot.answer_callback_query(call.id , 'У вас нет вакансий')
                    return
                
                support.employer.show_aplication(
                    bot , 
                    employer_id , 
                    job_id , 
                    app_id , 
                    index , 
                    call.message.message_id
                    
                )
                
            else:
                if call.data == 'employer_application_boundary_first':
                    bot.answer_callback_query(call.id, "Это крайний отклик", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайний отклик", show_alert=True)
        except Exception as e:
            logger.error(f'Error in navigation_application: {e}' , exc_info=True)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('employer_applocation_approv_'))
    @employer_only(bot , lambda msg: msg)
    def application_approv(call):
        try:
            app_id = call.data.split("_")[3]
            result = db.updata.approv_application(app_id)
            
            if result:
                bot.answer_callback_query(call.id , "Отклик принять" , show_alert=True)
                
                app = db.get.application_details(app_id)
                job = db.get.job_details(app['job_id'])
                
                db.updata.retention(job['employer_id'] , job['price'])
                
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

    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('employer_applocation_disapprov_'))
    @employer_only(bot , lambda msg: msg)
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
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
    @employer_only(bot , lambda msg: msg)
    def application_confirm(call):
        try:
            employer_id = int(call.message.chat.id)
            app_ids = db.get.app_ids_finish(int(call.data.split('_')[1]))
            
            if not app_ids:
                bot.send_message(employer_id , 'обратитесь в техническую поддержку')
                return
            
            support.employer.show_finished(bot , employer_id , int(call.data.split('_')[1]) , app_ids , 0 , call.message.message_id)
        
        except Exception as e:
            logger.error(f'Error in application_confirm: {e}' , exc_info=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('finished_'))
    @employer_only(bot , lambda msg: msg)
    def application_confirm1(call):
        try:
            _ , app_id , index , job_id , score = call.data.split('_')
            index , app_id , score = int(index) , int(app_id) , int(score)
            student_id = db.get.application_info(app_id , 'student_id')
            app_ids = db.get.app_ids_finish(job_id)
            amount = db.get.job_info(job_id , 'price')
            
            result1 = db.updata.user_rating(student_id , score)
            result2 = db.updata.job_confirm(app_id , (index+1 == len(app_ids)))
            
            if result1 and result2:
                bot.answer_callback_query(call.id , 'Оценка осавлена')
                
                db.updata.transfer(student_id , amount)
                
                support.employer.show_finished(bot , int(call.message.chat.id) , job_id , app_ids , 0 , call.message.message_id)
                
        except Exception as e:
            logger.error(f'Error in apllication_confirm1: {e}' , exc_info=True)
            
    
    @bot.message_handler(func=lambda m: m.text == "👥 Сотрудники")
    @employer_only(bot , lambda msg: msg)
    def my_staff(msg):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('➕добавить сотрудников' , '🙋‍♂️текущие сотрудники')
        bot.send_message(msg.chat.id , 'Вы хотите добавить сотрудника или просмотреть уже принятых сотрудников?' , reply_markup=markup)
     
    
    
    @bot.message_handler(func=lambda m: m.text == "🙋‍♂️текущие сотрудники")
    @employer_only(bot , lambda msg: msg)
    def my_staff(msg):
        all_staff = db.get.my_staff(msg.chat.id)
        
        if not all_staff:
            bot.send_message(msg.chat.id , 'у вас пока нет сотрудников')
        
        else:
            support.employer.my_staff(bot , msg.chat.id , 0 , msg.message_id)
    
    
    
    @bot.message_handler(func=lambda m: m.text == "➕добавить сотрудников")
    @employer_only(bot , lambda msg: msg)
    def add_staff(msg):
        all_staff = db.get.add_staff(msg.chat.id)
        
        if not all_staff:
            bot.send_message(msg.chat.id , 'пока нет заявок на добавления')
        
        else:
            support.employer.add_staff(bot , msg.chat.id , 0 , msg.message_id)
    
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('employer_addstaff_prev_' , 'employer_addstaff_boundary_first' , 'employer_addstaff_next_' , 'employer_addstaff_boundary_last')))
    @employer_only(bot , lambda msg: msg)
    def navigation_add_staff(call):
        try:
            if call.data.startswith(('employer_addstaff_prev_' , 'employer_addstaff_next_')):
                _ , _ , _ , staff_id , index , employer_id= call.data.split('_')
                all_staff = db.get.add_staff(employer_id)
                
                if not all_staff:
                    bot.answer_callback_query(call.id , 'Пока нет заявок на добалвние')
                    return
                
                new_staff_id = all_staff[index]
                
                support.employer.add_staff(bot , employer_id , index , call.message.message_id)
                
            else:
                if call.data == 'employer_addstaff_boundary_first':
                    bot.answer_callback_query(call.id, "Это крайная заявка", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайная заявка", show_alert=True)
        except Exception as e:
            logger.error(f'Error in navigation_add_staff: {e}')
    
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('employer_mystaff_prev_' , 'employer_mystaff_boundary_first' , 'employer_mystaff_next_' , 'employer_mystaff_boundary_last')))
    @employer_only(bot , lambda msg: msg)
    def navigation_my_staff(call):
        try:
            if call.data.startswith(('employer_mystaff_prev_' , 'employer_mystaff_next_')):
                _ , _ , _ , staff_id , index , employer_id= call.data.split('_')
                all_staff = db.get.my_staff(employer_id)
                
                if not all_staff:
                    bot.answer_callback_query(call.id , 'у вас пока нет сотрудников')
                    return
                
                new_staff_id = all_staff[index]
                
                support.employer.add_staff(bot , employer_id , index , call.message.message_id)
                
            else:
                if call.data == 'employer_addstaff_boundary_first':
                    bot.answer_callback_query(call.id, "Это крайний сотрудник", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Это крайний сотрудник", show_alert=True)
        except Exception as e:
            logger.error(f'Error in navigation_my_staff: {e}')


    @bot.callback_query_handler(func=lambda call: call.data.startswith('employer_mystaff_remove_'))
    @employer_only(bot , lambda msg: msg)
    def remove_staff(call):
        try:
            staff_id = call.data.split('_')[3]
            db.updata.remove_staff(staff_id)
            bot.answer_callback_query(call.id , 'сотрудник уволин' , show_alert=True)
            logger.info(f'User: {staff_id} remove')
            
        except Exception as e:
            logger.error(f'Error in remove_staff: {e}')
    


    @bot.callback_query_handler(func=lambda call: call.data.startswith('employer_addstaff_approv_'))
    @employer_only(bot , lambda msg: msg)
    def approv_add_staff(call):
        try:
            staff_id = call.data.split('_')[3]
            db.updata.adding_staff(staff_id)
            bot.answer_callback_query(call.id , 'Пользователь принять' , show_alert=True)
            logger.info(f'User: {staff_id} accept')
            
        except Exception as e:
            logger.error(f'Error in approved_add_staff: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('employer_addstaff_disapprov_'))
    @employer_only(bot , lambda msg: msg)
    def approv_add_staff(call):
        try:
            staff_id = call.data.split('_')[3]
            db.updata.not_adding_staff(staff_id)
            bot.answer_callback_query(call.id , 'Заявка отлонена' , show_alert=True)
            logger.info(f'User: {staff_id} does not accept')
            
        except Exception as e:
            logger.error(f'Error in approved_add_staff: {e}')
            
    
    
    @bot.message_handler(func=lambda m: m.text == "💳 Пополнить баланс")
    @employer_only(bot , lambda msg: msg)
    def start_topup(msg):
            bot.send_message(msg.chat.id , 'Введите сумму пополнения')
            bot.register_next_step_handler(msg , get_amount)
    
    
    def get_amount(msg):
        try:
            amount = round(float(msg.text) * (1 + commission_rate), 2)
            bot.delete_state(msg.chat.id , msg.chat.id)
            bot.set_state(msg.from_user.id , 'process_create' , msg.chat.id)
            bot.add_data(msg.from_user.id , msg.chat.id , amount = amount)
            bot.add_data(msg.from_user.id , msg.chat.id , amount1 = float(msg.text))
            
            
            bot.send_message(
                msg.chat.id,
                f"💳 *Пополнение баланса*\n\n"
                f"С учётом комиссии (5%) вам необходимо перевести *{amount} ₽* на следующий счёт:\n\n"
                f"📌 *Реквизиты для перевода:*\n"
                f"`1234 5678 9012 3456`\n\n"
                f"После перевода, пожалуйста, отправьте *PDF-файл с чеком* в этом чате для подтверждения транзакции.",
            )
            bot.register_next_step_handler(msg, get_receipt)
            
        except ValueError:
            bot.send_message(msg.chat.id, "Пожалуйста, введите корректную сумму.")
            bot.register_next_step_handler(msg, get_amount)
    
    
    def get_receipt(msg):
        if not msg.document or not msg.document.file_name.endswith('.pdf'):
            bot.send_message(msg.chat.id, "Пожалуйста, отправьте именно PDF-файл.")
            bot.register_next_step_handler(msg, get_receipt)
            return

        user_id = msg.from_user.id
        name = db.get.user_info(user_id , 'name')
        username = db.get.user_info(user_id , 'user_name')

        with bot.retrieve_data(msg.from_user.id , msg.chat.id) as data:
            if not data:
                bot.send_message(msg.chat.id, "Что-то пошло не так. Попробуйте снова")
                return

            amount = data['amount']
            amount1 = data['amount1']
            

        # Отправка в модераторский чат
        caption = (
            f"📥 Заявка на пополнение\n"
            f"👤 Пользователь: {name} (@{username})\n"
            f"🆔 ID: {user_id}\n"
            f"💳 Сумма пополнения c учётом комисии: {amount} ₽\n"
            f"📂 Чек приложен ниже\n"
        )

        markup = types.InlineKeyboardMarkup()
        approv_btn = types.InlineKeyboardButton('✅подтвердить' , callback_data=f'aproved_topup_{msg.chat.id}_{amount1}')
        disapprov_btn = types.InlineKeyboardButton('❌отклонить' , callback_data=f'disaproved_topup_{msg.chat.id}_{amount1}')
        markup.row(approv_btn , disapprov_btn)
        
        file_id = msg.document.file_id
        bot.send_document(chat_id=chat_mod, document=file_id, caption=caption)
        bot.send_message(chat_id=chat_mod, text="Что сделать с заявкой?", reply_markup=markup)

        bot.send_message(msg.chat.id, "Заявка отправлена модераторам. Ожидайте подтверждения.")
        logger.info(f'request for replenishment from: {msg.chat.id}')
    
    
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

        
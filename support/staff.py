from telebot import TeleBot, types
import logging
import data_base as db
import keyboards

logger = logging.getLogger(__name__)



class staff:
    def show_job(bot: TeleBot, staff_id: int, job_id: int, current_index: int, msg_id: int):
        try:
            job = db.get.job_details(job_id)
            all_job_id = db.get.staff_job(staff_id)
            total_jobs = all_job_id
            markup = types.InlineKeyboardMarkup()
            btns = keyboards.staff.job(current_index , total_jobs , all_job_id)
            
            status_info = {
                'open' : ('поиск кондидатов' , True) , 
                'wait' : ('ожидает выполнения' , True) , 
                'in_progress' : ('в процессе выполнения' , True) , 
                'done' : ('ожидает подтверждения выполненной работы' , None) , 
                'completed' : ('завершино' , None)
                
            }
            
            status_text , show_executer = status_info.get(job['status'] , ('Неизвестный статус' , None))
            message = str(
                f'название вакансии: {job['title']}\n\n'
                f'статус: {status_text}'
            )
            
            if show_executer:
                app_ids = db.get.approved_application_ids(job_id)
                if app_ids:
                    message += f'\nколичество исполнителей: {len(app_ids)}/{job['people']}'
            
            staff = db.get.user_info(job['staff'] , 'name')
            message += str(
                '\n=======================\n'
                f"📅 <b>Дата:</b> {job['date']}\n"
                f"⏰ <b>Время:</b> {job['start_time']}–{job['finish_time']}\n"
                f"💰 <b>Оплата:</b> {job['price']} ₽\n"
                f"👤 <b>Ответственный:</b> {staff}\n\n"
                f"📝 <b>Описание:</b> {job['description']}"
            )
            
            if job['status'] == 'open':
                btn = types.InlineKeyboardButton('👤кондидаты' , callback_data=f'staffcandidates_{job_id}')
                markup.row(btns[0] , btn , btns[1])
            
            elif job['status'] in ('wait' , 'in_progress'):
                markup.row(btns[0] , btns[1])
            
            elif job['status'] == 'done':
                btn = types.InlineKeyboardButton('✅подтвердить' , callback_data=f'staffconfirm_{job_id}')
                markup.row(btns[0] , btn , btns[1])
            
            elif job['status'] == 'comleted':
                btn = types.InlineKeyboardButton('⭐оценить' , callback_data=f'staffestimate_{job_id}')
                markup.row(btns[0] , btn , btns[1])
            
            try:
                bot.edit_message_text(
                    chat_id = staff_id , 
                    message_id = msg_id , 
                    text = message , 
                    reply_markup= markup ,
                    parse_mode= "HTML"
                )
            except:
                bot.send_message(staff_id , message , reply_markup=markup , parse_mode='HTML')
            
                
            
        except Exception as e:
            logger.error(f'Error in support.employer.show_job: {e}')
    
    
    def show_aplication(bot: TeleBot , staff_id: int , job_id: int , app_id: int , current_index: int , msg_id: int):
        try:
            app = db.get.application_details(app_id)
            all_app = db.get.application_by_job(job_id)
            
            if not app:
                bot.send_message(staff_id , 'откликов пока не найдено')
                return
            
            rating = app['rating_sum']/app['rating_number']
            
            if int(rating) == rating:
                rating = int(rating)
                
            else:
                rating = round(rating, 2)
            
            message = str(
                f'кондидат: {app['student_name']}\n'
                '=======================\n\n'
                f'рейтинг: {rating}\n'
                f'ранее выполненных работ: {app['rating_number']-1}'
            )
            
            btns = keyboards.staff.application(current_index , all_app , job_id)
            markup = types.InlineKeyboardMarkup()
            markup.row(btns[0] , btns[1] , btns[2] , btns[3])
            
            bot.send_message(
                staff_id , 
                message , 
                'HTML' , 
                reply_markup=markup
            )
        
        except Exception as e:
            logger.error(f'Error in show_aplication: {e}')
    
    
    def show_finished(bot , employer_id , job_id , app_ids , index , msg_id):
        try:
            if not app_ids:
                bot.send_message(employer_id , 'обратитесь в техническую поддержку')
                return
            
            if len(app_ids) == index:
                try:
                    bot.edit_message_text(
                        chat_id = employer_id , 
                        message_id = msg_id , 
                        text = 'вы оценили всех сотрудников' , 
                        parse_mode= "HTML"
                    )
                except:
                    bot.send_message(employer_id , 'вы оценили всех сотрудников' , parse_mode='HTML')
                return
            
            app = db.get.application_details(app_ids[index])
            rating = app['rating_sum']/app['rating_number']
            
            if int(rating) == rating:
                rating = int(rating)
                
            else:
                rating = round(rating, 2)
            
            message = str(
                f'исполнитель: {app['student_name']}\n'
                '=======================\n\n'
                f'рейтинг: {rating}\n'
                f'ранее выполненных работ: {app['rating_number']}\n\n'
                'Оцените работу пользователя по 5 бальной шкале, число должно быть целым'
            )
            
            markup = types.InlineKeyboardMarkup()
            btns = keyboards.staff.finished(index , app_ids , job_id)
            for i in btns:
                markup.row(i)
            
            try:
                bot.edit_message_text(
                    chat_id = employer_id , 
                    message_id = msg_id , 
                    text = message , 
                    reply_markup= markup ,
                    parse_mode= "HTML"
                )
            except:
                bot.send_message(employer_id , message , reply_markup=markup , parse_mode='HTML')
            
            
        
        except Exception as e:
            logger.error(f'Error in show_finished: {e}' , exc_info=True)
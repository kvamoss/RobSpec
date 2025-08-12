from telebot import TeleBot, types
import logging
import data_base as db
import keyboards

logger = logging.getLogger(__name__)



class student:
    def show_job(bot: TeleBot , student_id: int , job_id: int , index:int , msg_id: int):
        try:
            job = db.get.job_details(job_id)
            if not job:
                bot.send_message(student_id , 'вакансия не найдена')
                return

            all_jobs = db.get.job_ids()
            total_jobs = all_jobs
            employer_id = job['employer_id']
            star = db.get.user_info(employer_id , 'rating_sum')/ db.get.user_info(employer_id , 'rating_number')
            
            message = str(
                f'название вакансии: {job['title']}\n'
                '\n=======================\n'
                f"📅 <b>Дата:</b> {job['date']}\n"
                f"⏰ <b>Время:</b> {job['start_time']}–{job['finish_time']}\n"
                f"💰 <b>Оплата:</b> {job['price']} ₽\n"
                f"📝 <b>Описание:</b> {job['description']}"
            )

            markup = types.InlineKeyboardMarkup(row_width=3)
            btns = keyboards.student.job(index , total_jobs , all_jobs)
            markup.row(btns[0] , btns[1] , btns[2])
            
            try:
                bot.edit_message_text(
                    chat_id = student_id , 
                    message_id = msg_id , 
                    text = message , 
                    reply_markup= markup , 
                    parse_mode= "HTML"
                )
            except:
                bot.send_message(student_id , message , reply_markup=markup , parse_mode='HTML')
        except Exception as e:
            logger.error(f'Error in support.student.show_job: {e}')
    
    
    def my_job(bot: TeleBot , student_id: int , app_id: int , index: int , msg_id: int):
        try:
            job_id = db.get.application_info(app_id , 'job_id')
            if not job_id:
                bot.send_message(student_id , 'Вакансия не найдена')
                return
            
            app_ids = db.get.applications_student(student_id)
            job = db.get.job_details(job_id)
            app_status = db.get.application_info(app_id , 'status')
            rating = db.get.user_info(job['employer_id'] , 'rating_sum') / db.get.user_info(job['employer_id'] , 'rating_number')
            
            if int(rating) == rating:
                rating = int(rating)
                
            else:
                rating = round(rating, 2)
            
            markup = types.InlineKeyboardMarkup()
            btns = keyboards.student.my_job(index , app_ids)
            
            if app_status == 'accepted':
                message = str(
                    'Статус: поддтвержденно\n'
                    f'заказчик: {job['employer_name']} {rating} ⭐\n'
                    f'название: {job['title']}'
                    '\n=======================\n'
                    f"📅 <b>Дата:</b> {job['date']}\n"
                    f"⏰ <b>Время:</b> {job['start_time']}–{job['finish_time']}\n"
                    f"💰 <b>Оплата:</b> {job['price']} ₽\n"
                    f"📝 <b>Описание:</b> {job['description']}\n\n"
                    'для того что бы начать выполнять работу нажмитие на кнопку "начать"'
                )
                
                btn = types.InlineKeyboardButton('Начать' , callback_data=f"start_{app_id}_{index}")
                markup.row(btns[0] , btn , btns[1])
            
            elif app_status == 'start':
                message = str(
                    'Статус: в процессе\n'
                    f'заказчик: {job['employer_name']} {str(rating) + '⭐'}\n'
                    f'название: {job['title']}'
                    '\n=======================\n'
                    f"📅 <b>Дата:</b> {job['date']}\n"
                    f"⏰ <b>Время:</b> {job['start_time']}–{job['finish_time']}\n"
                    f"💰 <b>Оплата:</b> {job['price']} ₽\n"
                    f"📝 <b>Описание:</b> {job['description']}\n\n"
                    'для того что бы начать выполнять работу нажмитие на кнопку "начать"'
                )
                
                btn = types.InlineKeyboardButton('закончить' , callback_data=f"finish_{app_id}_{index}")
                markup.row(btns[0] , btn , btns[1])
            
            
            elif app_status == 'finish':
                message = str(
                    'Статус: ожидает подтверждения\n'
                    f'заказчик: {job['employer_name']} {str(rating) + '⭐'}\n'
                    f'название: {job['title']}\n'
                    '\n=======================\n'
                    f"📅 <b>Дата:</b> {job['date']}\n"
                    f"⏰ <b>Время:</b> {job['start_time']}–{job['finish_time']}\n"
                    f"💰 <b>Оплата:</b> {job['price']} ₽\n"
                    f"📝 <b>Описание:</b> {job['description']}\n\n"
                    'для того что бы начать выполнять работу нажмитие на кнопку "начать"'
                )
                markup.row(btns[0] , btns[1])
                
            elif app_status == 'done':
                message = str(
                    'Статус: заверщино\n'
                    f'заказчик: {job['employer_name']} {str(rating) + '⭐'}\n'
                    f'название: {job['title']}\n'
                    '\n=======================\n'
                    f"📅 <b>Дата:</b> {job['date']}\n"
                    f"⏰ <b>Время:</b> {job['start_time']}–{job['finish_time']}\n"
                    f"💰 <b>Оплата:</b> {job['price']} ₽\n"
                    f"📝 <b>Описание:</b> {job['description']}\n\n"
                    'для того что бы начать выполнять работу нажмитие на кнопку "начать"'
                )
                
                btn = types.InlineKeyboardButton('оценить' , callback_data=f"comleted_{index}_{app_id}_{student_id}")
                markup.row(btns[0] , btn , btns[1])
            
            else:
                logger.error(f'unknown status in support.student.my_job: {app_status}')
            
            
            try:
                bot.edit_message_text(
                    chat_id = student_id , 
                    message_id = msg_id , 
                    text = message , 
                    reply_markup= markup , 
                    parse_mode= "HTML"
                )
            except:
                bot.send_message(student_id , message , reply_markup=markup , parse_mode='HTML')
        
        except Exception as e:
            logger.error(f'Error in support.student.my_job: {e}' , exc_info=True)

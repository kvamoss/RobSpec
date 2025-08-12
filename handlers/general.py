from telebot import types
from telebot import TeleBot
import random
import string

from . import student , admin , employer , mod , staff 
import logging
import data_base as db
import keyboards

logger = logging.getLogger(__name__)


def generate_secret_code(length=5):
    """Генератор секретного кода из латинских букв (A-Z, a-z)"""
    characters = string.ascii_letters  # Все латинские буквы (A-Za-z)
    return ''.join(random.choice(characters) for _ in range(length))

def home(bot , user_id):
    role = db.get.user_info(user_id , 'role')

    if role == 'student':
        student.student_home_page(bot , user_id)

    if role == 'employer':
        employer.emplouer_home_page(bot , user_id)
    
    if role == 'staff':
        staff.staff_home_page(bot , user_id)


def register_general(bot: TeleBot):
    
    @bot.message_handler(commands=['start'])
    def handle_start(msg):
        try:
            if not db.user_exists(msg.from_user.id):
                bot.delete_state(msg.from_user.id, msg.chat.id)
                bot.set_state(msg.from_user.id, "add_user", msg.chat.id)

                message = str(
                    '<b>👋 Добро пожаловать в <u>RobSpec</u>!</b>\n\n'
                    'Пожалуйста, выберите вашу <b>роль</b> в системе:\n'  
                    '▫️ <b>исполнитель</b> — ищет подработку  \n'
                    '▫️ <b>Работодатель</b> — публикует вакансии\n'  
                    '▫️ <b>Сотрудник</b> — помогает работодателю\n\n'
                    '<b>Нажмите на кнопку ниже, чтобы продолжить.</b>'
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message  , 
                    reply_markup=keyboards.general.role_keyboard() , 
                    parse_mode='HTML'
                    )
                
                logger.info(f'user: {msg.chat.id} started register')
                bot.register_next_step_handler(msg , process_select_name)
            
            else:
                role = db.get.user_info(msg.from_user.id , 'role')

                if role == 'student':
                    student.student_home_page(bot , msg.from_user.id)

                if role == 'employer':
                    employer.emplouer_home_page(bot , msg.from_user.id)
                
                if role == 'staff':
                    staff.staff_home_page(bot , msg.from_user.id)


        
        except Exception as e:
            logger.error(f'Error in handle_start: {e}')
    

    def process_select_name(msg):
        try:
            if not(msg.text in ("📢 Заказчик" , "🧑‍💻 Исполнитель" , "🏢сотрудник")):
                message = str(
                    "<b>❗ Пожалуйста, выберите вашу роль:</b>\n\n"
                    "👇 Нажмите одну из кнопок ниже, чтобы продолжить:\n"
                    "▪️ <b>💼 Заказчик</b> — хочу разместить проект\n"
                    "▪️ <b>🛠️ Исполнитель</b> — ищу задачи для выполнения"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode="HTML"
                    )
                bot.register_next_step_handler(msg , process_select_name)

            else:
                if msg.text == '📢 Заказчик':
                    bot.add_data(msg.from_user.id , msg.chat.id , role = 'employer')
                    message = str(
                        '<b>🏢 Название компании или ИП</b>\n\n'
                        'Введите название, например:\n'  
                        '<code>ИП Смирнов</code> или <code>ООО "РобСкеп"</code>\n\n'
                        'Оно будет показываться в карточках вакансий.\n\n'
                        'для отмены введите /cancle'
                    )

                elif msg.text == '🧑‍💻 Исполнитель':
                    bot.add_data(msg.from_user.id , msg.chat.id , role = 'student')
                    message = str(
                        '<b>✍️ Как к вам оброщаться</b>\n\n'
                        'Введите <u>полное имя</u> в формате:\n' 
                        '<code>Иванов Иван Иванович</code>\n\n'
                        'Это имя будет отображаться другим пользователям.\n\n'
                        'для отмены введите /cancle'
                    )

                elif msg.text == '🏢сотрудник':
                    bot.add_data(msg.from_user.id , msg.chat.id , role = 'staff')
                    message = str(
                        '<b>✍️ Как к вам оброщаться</b>\n\n'
                        'Введите <u>полное имя</u> в формате:\n' 
                        '<code>Иванов Иван Иванович</code>\n\n'
                        'Это имя будет отображаться другим пользователям.\n\n'
                        'для отмены введите /cancle'
                    )
                
                bot.send_message(msg.chat.id , message , parse_mode='HTML' , reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg , process_register_finish)


        except Exception as e:
            logger.error(f'Error in process_select_name: {e}')


    def process_register_finish(msg):
        try:
            if msg.text == '/cancle':
                message = str(
                    "<b>❗ Пожалуйста, выберите вашу роль:</b>\n\n"
                    "👇 Нажмите одну из кнопок ниже, чтобы продолжить:\n"
                    "▪️ <b>💼 Заказчик</b> — хочу разместить проект\n"
                    "▪️ <b>🛠️ Исполнитель</b> — ищу задачи для выполнения"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode="HTML"
                    )
                return bot.register_next_step_handler(msg , process_select_name)
                
            with bot.retrieve_data(msg.from_user.id , msg.chat.id) as data:
                if data['role'] == 'employer':
                    new_code = ''
                    while db.check.is_secret_code_exists(new_code) or new_code == '':
                        new_code = generate_secret_code()
                        
                    db.add.user(
                    msg.from_user.id , 
                    msg.from_user.username , 
                    msg.text , 
                    data['role'] , 
                    secret_code = new_code
                    )

                else:
                    db.add.user(
                        msg.from_user.id , 
                        msg.from_user.username , 
                        msg.text , 
                        data['role'] , 
                    )
            
            home(bot , msg.from_user.id)
        
        except Exception as e:
            logger.error(f'Error in process_register_finish: {e}')
from typing import Union
from telebot import types
import data_base as db


class employer:
    
    def home()->types.ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True , one_time_keyboard=True)
        markup.add("➕ Создать вакансию" , "📋 Мои вакансии" , "👥 Сотрудники" , "💳 Пополнить баланс" , "🛠 Техподдержка")

        return markup

    def staff(secret_code: str)-> types.ReplyKeyboardMarkup:
        staff_list = db.get.staff(secret_code)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True , one_time_keyboard=True)
        
        for i in staff_list:
            markup.add(i['name'])
        
        return markup
    
    def job(current_index, total_jobs, all_job_ids):
        total_jobs , current_index= len(total_jobs) , int(current_index)
        if current_index > 0:
            prev_id = all_job_ids[current_index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"employer_project_prev_{prev_id}_{current_index-1}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="employer_project_boundary_first"
            )
        
        # Кнопка "вперед"
        if current_index < total_jobs - 1:
            next_id = all_job_ids[current_index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"employer_project_next_{next_id}_{current_index+1}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="employer_project_boundary_last"
            )

        return [btn_back, btn_next]
    
    
    def application(current_index , all_app_ids , job_id):
        total_jobs = len(all_app_ids)
        if current_index > 0:
            prev_id = all_app_ids[current_index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"employer_application_prev_{prev_id}_{current_index-1}_{job_id}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="employer_application_boundary_first"
            )
        
        # Кнопка "вперед"
        if current_index < total_jobs - 1:
            next_id = all_app_ids[current_index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"employer_applocation_next_{next_id}_{current_index+1}_{job_id}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="employer_application_boundary_last"
            )

        btn_approv = types.InlineKeyboardButton("✅подтвердить" , callback_data= f'employer_applocation_approv_{all_app_ids[current_index]}')
        btn_disapprove = types.InlineKeyboardButton("❌отклонить" , callback_data= f'employer_applocation_disapprov_{all_app_ids[current_index]}')
        return [btn_back , btn_approv , btn_disapprove , btn_next]
    
    
    def finished(index , all_app_ids , job_id):

        btns = (
                types.InlineKeyboardButton('1' , callback_data=f'finished_{all_app_ids[index]}_{index}_{job_id}_1') , 
                types.InlineKeyboardButton('2' , callback_data=f'finished_{all_app_ids[index]}_{index}_{job_id}_2') , 
                types.InlineKeyboardButton('3' , callback_data=f'finished_{all_app_ids[index]}_{index}_{job_id}_3') , 
                types.InlineKeyboardButton('4' , callback_data=f'finished_{all_app_ids[index]}_{index}_{job_id}_4') , 
                types.InlineKeyboardButton('5' , callback_data=f'finished_{all_app_ids[index]}_{index}_{job_id}_5') , 
            )
        
        return btns
    
    
    
    def add_staff(index , all_staff , employer_id):
        total_jobs = len(all_staff)
        if index > 0:
            prev_id = all_staff[index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"employer_addstaff_prev_{prev_id}_{index-1}_{employer_id}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="employer_addstaff_boundary_first"
            )
        
        # Кнопка "вперед"
        if index < total_jobs - 1:
            next_id = all_staff[index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"employer_addstaff_next_{next_id}_{index+1}_{employer_id}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="employer_addstaff_boundary_last"
            )

        btn_approv = types.InlineKeyboardButton("✅принять" , callback_data= f'employer_addstaff_approv_{all_staff[index]}')
        btn_disapprove = types.InlineKeyboardButton("❌отклонить" , callback_data= f'employer_addstaff_disapprov_{all_staff[index]}')
        return [btn_back , btn_approv , btn_disapprove , btn_next]
    
    
    def my_staff(index , all_staff , employer_id):
        total_jobs = len(all_staff)
        if index > 0:
            prev_id = all_staff[index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"employer_mystaff_prev_{prev_id}_{index-1}_{employer_id}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="employer_mystaff_boundary_first"
            )
        
        # Кнопка "вперед"
        if index < total_jobs - 1:
            next_id = all_staff[index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"employer_mystaff_next_{next_id}_{index+1}_{employer_id}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="employer_mystaff_boundary_last"
            )

        btn_remove = types.InlineKeyboardButton("❌Уволить" , callback_data= f'employer_mystaff_remove_{all_staff[index]}')
        return [btn_back , btn_remove , btn_next]
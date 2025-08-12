from typing import Union
from telebot import types
import data_base as db

class staff:
    def staff_home():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True , one_time_keyboard=True)
        markup.add("📂 Мои вакансии" , "🛠 Техподдержка")

        return markup
    
    
    def job(current_index, total_jobs, all_job_ids):
        total_jobs , current_index= len(total_jobs) , int(current_index)
        if current_index > 0:
            prev_id = all_job_ids[current_index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"staff_project_prev_{prev_id}_{current_index-1}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="staff_project_boundary_first"
            )
        
        # Кнопка "вперед"
        if current_index < total_jobs - 1:
            next_id = all_job_ids[current_index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"staff_project_next_{next_id}_{current_index+1}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="staff_project_boundary_last"
            )

        return [btn_back, btn_next]
    
    
    def application(current_index , all_app_ids , job_id):
        total_jobs = len(all_app_ids)
        if current_index > 0:
            prev_id = all_app_ids[current_index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"staff_application_prev_{prev_id}_{current_index-1}_{job_id}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="staff_application_boundary_first"
            )
        
        # Кнопка "вперед"
        if current_index < total_jobs - 1:
            next_id = all_app_ids[current_index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"staff_applocation_next_{next_id}_{current_index+1}_{job_id}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="staff_application_boundary_last"
            )

        btn_approv = types.InlineKeyboardButton("✅подтвердить" , callback_data= f'staff_applocation_approv_{all_app_ids[current_index]}')
        btn_disapprove = types.InlineKeyboardButton("❌отклонить" , callback_data= f'staff_applocation_disapprov_{all_app_ids[current_index]}')
        return [btn_back , btn_approv , btn_disapprove , btn_next]
    
    
    def finished(index , all_app_ids , job_id):

        btns = (
                types.InlineKeyboardButton('1' , callback_data=f'staffinished_{all_app_ids[index]}_{index}_{job_id}_1') , 
                types.InlineKeyboardButton('2' , callback_data=f'stafffinished_{all_app_ids[index]}_{index}_{job_id}_2') , 
                types.InlineKeyboardButton('3' , callback_data=f'stafffinished_{all_app_ids[index]}_{index}_{job_id}_3') , 
                types.InlineKeyboardButton('4' , callback_data=f'stafffinished_{all_app_ids[index]}_{index}_{job_id}_4') , 
                types.InlineKeyboardButton('5' , callback_data=f'stafffinished_{all_app_ids[index]}_{index}_{job_id}_5') , 
            )
        
        return btns
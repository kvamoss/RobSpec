from typing import Union
from telebot import types

class student:
    
    def home()->types:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True , one_time_keyboard=True)
        markup.add('🔍 Поиск вакансий' , '📄 Мои работы' , '💸 Вывести средства' , '🛠 Техподдержка')

        return markup
    
    
    def job(current_index, total_jobs, all_job_ids):
        total_jobs = len(total_jobs)
        if current_index > 0:
            prev_id = all_job_ids[current_index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"student_project_prev_{prev_id}_{current_index-1}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="student_project_boundary_first"
            )
        
        # Кнопка "вперед"
        if current_index < total_jobs - 1:
            next_id = all_job_ids[current_index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"student_project_next_{next_id}_{current_index+1}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="student_project_boundary_last"
            )
        
        btn_apply = types.InlineKeyboardButton("✅ откликнуться" , callback_data=f"apply_job_{all_job_ids[current_index]}")

        return [btn_back , btn_apply , btn_next]
    
    
    def my_job(current_index , all_job_ids):
        total_jobs = len(all_job_ids)
        
        if current_index > 0:
            prev_id = all_job_ids[current_index - 1]
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data=f"student_myjob_prev_{prev_id}_{current_index-1}"
            )
        else:
            btn_back = types.InlineKeyboardButton(
                "⏮️ назад", 
                callback_data="student_myjob_boundary_first"
            )
        
        # Кнопка "вперед"
        if current_index < total_jobs - 1:
            next_id = all_job_ids[current_index + 1]
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data=f"student_myjob_next_{next_id}_{current_index+1}"
            )
        else:
            btn_next = types.InlineKeyboardButton(
                "вперёд ⏭️", 
                callback_data="student_myjob_boundary_last"
            )

        return [btn_back , btn_next]


    def finished(index , all_app_ids , job_id):

        btns = (
                types.InlineKeyboardButton('1' , callback_data=f'comlet_{all_app_ids[index]}_{index}_{job_id}_1') , 
                types.InlineKeyboardButton('2' , callback_data=f'comlet_{all_app_ids[index]}_{index}_{job_id}_2') , 
                types.InlineKeyboardButton('3' , callback_data=f'comlet_{all_app_ids[index]}_{index}_{job_id}_3') , 
                types.InlineKeyboardButton('4' , callback_data=f'comlet_{all_app_ids[index]}_{index}_{job_id}_4') , 
                types.InlineKeyboardButton('5' , callback_data=f'comlet_{all_app_ids[index]}_{index}_{job_id}_5') , 
            )
        
        return btns
    
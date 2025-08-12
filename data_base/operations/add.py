import sqlite3
from typing import Union
import logging
from data_base.core import get_connection , logger


def user(user_id: int , username: str , name: str , role: str , balance: float=0 , secret_code: str=None):
    """добавляет нового пользователя"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO
                users (user_id , user_name , name , balance , role , secret_code) VALUES (? , ? , ? , ? , ? , ?) 
            """ , (user_id , username , name , balance , role , secret_code))
        
            conn.commit()
            logger.info(f'new user ({user_id})')
        
    except Exception as e:
        logger.error(f'Error in add.user: {e}')


def job(employer_id , title , description , time_start , time_finish , date ,  price , people , staff_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO jobs(
                employer_id , 
                title , 
                description , 
                date , 
                start_time , 
                finish_time , 
                price ,
                people ,  
                staff , 
                status 
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ( 
            int(employer_id),
            str(title),
            str(description),
            str(date),
            str(time_start),
            str(time_finish),
            float(price),
            int(people),
            int(staff_id),
            'open'
            ))


            conn.commit()
            
            logger.info(f'new job from user:{employer_id}')
        
    except Exception as e:
        logger.error(f'Error in add.job: {e}')



def application(job_id , student_id):
    """Создает новый отклик на проект"""

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Проверяем существование студента
            cursor.execute("SELECT 1 FROM users WHERE user_id = ? AND role = 'student'", (student_id,))
            if not cursor.fetchone():
                return 'студент не найден'
            
            # 2. Проверяем дубликат отклика
            cursor.execute("""
                SELECT 1 FROM applications 
                WHERE job_id = ? AND student_id = ?
                LIMIT 1
            """, (job_id, student_id))
            
            if cursor.fetchone():
                return 'вы уже откликнулись на эту вакансию'
            
            # 3. Получаем информацию о заказчике и проверяем проект
            cursor.execute("""
                SELECT u.user_id, u.user_name 
                FROM jobs j
                JOIN users u ON j.employer_id = u.user_id
                WHERE j.job_id = ?
            """, (job_id,))
            
            employer_data = cursor.fetchone()
            
            if not employer_data:
                return 'проект не найден'

            # 4. Создаем заявку
            cursor.execute("""
                INSERT INTO applications (job_id, student_id, status, created_at)
                VALUES (?, ?, 'pending', datetime('now'))
            """, (job_id, student_id))
            
            conn.commit()
            
            return 'Ваш отклик успешно отправлен'
            
    except Exception as e:
        logger.error(f'Error in add.application: {e}')
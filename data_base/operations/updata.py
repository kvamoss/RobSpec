import sqlite3
from typing import Union , Optional
import logging
from data_base.core import get_connection , logger


def approv_application(app_id: int) -> bool:
    
    
    try:
         with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT job_id FROM applications WHERE app_id = ?", (app_id,))
            result = cursor.fetchone()
            job_id = result[0]
            
            # 1. Обновляем статусы откликов
            cursor.execute("""
                UPDATE applications 
                SET status = ?
                WHERE app_id = ?
            """, ('accepted', app_id))
            
            # 2. Проверяем, набралось ли достаточно подтверждённых откликов
            cursor.execute("""
                UPDATE jobs
                SET status = CASE 
                    WHEN (
                        SELECT COUNT(*) 
                        FROM applications a 
                        WHERE a.job_id = jobs.job_id AND a.status = 'accepted'
                    ) >= jobs.people THEN 'wait'
                    ELSE jobs.status
                END
                WHERE job_id = ?;
            """, (job_id,))
            
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f'Error in approv_application: {e}')
        return False
    finally:
        cursor.close()
           

def disapprov_application(app_id: int) -> bool:
    
    
    try:
         with get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Обновляем статусы откликов
            cursor.execute("""
                UPDATE applications 
                SET status = ?
                WHERE app_id = ?
            """, ('canceled', app_id))
            
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f'Error in disapprov_application: {e}')
        return False
    finally:
        cursor.close()


def start_jobs(app_id: int , time) -> bool:
    
    
    try:
         with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT job_id FROM applications WHERE app_id = ?", (app_id,))
            result = cursor.fetchone()
            job_id = result[0]
            
            # 1. Обновляем статусы откликов
            cursor.execute("""
                UPDATE applications 
                SET status = ? , start = ?
                WHERE app_id = ?
            """, ('start', time , app_id))
            
            # 2. Обновляем статус вакансии
            cursor.execute("""
                UPDATE jobs
                SET status = ?
                WHERE job_id = ?
            """, ('in_progress', job_id))
            
            conn.commit()
            return job_id
    except Exception as e:
        conn.rollback()
        logger.error(f'Error in start_jobs: {e}')
        return False
    finally:
        cursor.close()


def finish_jobs(app_id: int , time) -> bool:
    
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT job_id FROM applications WHERE app_id = ?", (app_id,))
            result = cursor.fetchone()
            job_id = result[0]
            cursor.execute("SELECT people FROM jobs WHERE job_id = ?" , (job_id , ))
            people = cursor.fetchone()[0]
            cursor.execute("""SELECT COUNT(*)
                            FROM applications
                            WHERE job_id = ? AND status ='finish'
                        """ , (job_id , ))
            done = cursor.fetchone()[0]
            
            # 1. Обновляем статусы откликов
            cursor.execute("""
                UPDATE applications 
                SET status = ? , finish = ?
                WHERE app_id = ?
            """, ('finish', time , app_id))
            
            if people-1 == done:
                # 2. Обновляем статус вакансии
                cursor.execute("""
                    UPDATE jobs
                    SET status = ?
                    WHERE job_id = ?
                """, ('done', job_id))
            
            conn.commit()
            return job_id
    except Exception as e:
        conn.rollback()
        logger.error(f'Error in finish_jobs: {e}')
        return False
    finally:
        cursor.close()
    

def user_rating(user_id , score):
    
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            #обновляем рейтинг
            cursor.execute("""
            UPDATE users
            SET rating_sum = rating_sum + ? , rating_number = rating_number + 1
            WHERE user_id = ?
            """ , (score , user_id))

            conn.commit()
            return True
    
    except Exception as e:
        logger.error(f'Error in updata.user_rating: {e}')
        return False
    
    
def job_confirm(app_id: int , end) -> bool:
    
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT job_id FROM applications WHERE app_id = ?", (app_id,))
            result = cursor.fetchone()
            job_id = result[0]
            
            # 1. Обновляем статусы откликов
            cursor.execute("""
                UPDATE applications 
                SET status = ?
                WHERE app_id = ?
            """, ('done' , app_id))
            
            if end:
                # 2. Обновляем статус вакансии
                cursor.execute("""
                    UPDATE jobs
                    SET status = ?
                    WHERE job_id = ?
                """, ('completed', job_id))
            
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f'Error in finish_jobs: {e}' , exc_info=True)
        return False
    finally:
        cursor.close()
        
def application_confirm(app_id: int) -> bool:
    print(app_id)
    
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # 1. Обновляем статусы откликов
            cursor.execute("""
                UPDATE applications 
                SET status = ?
                WHERE app_id = ?
            """, ('completed' , app_id))

            
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f'Error in finish_jobs: {e}')
        return False
    finally:
        cursor.close()


def join_employer(user_id, secret_code):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
           SELECT user_id from users  WHERE secret_code = ?
        """, (secret_code, ))
        result = cursor.fetchone()[0]
        
        cursor.execute("""
            UPDATE users
            SET secret_code = ?
            WHERE user_id = ?
        """, (f"!{secret_code}" , user_id))
        conn.commit()
    
    return result

def adding_staff(staff_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT secret_code from users  WHERE user_id = ?
            """, (staff_id, ))
        secret_code = cursor.fetchone()[0][1:]
            
        cursor.execute("""
            UPDATE users
            SET secret_code = ?
            WHERE user_id = ?
        """, (secret_code , staff_id))
        conn.commit()


def remove_staff(staff_id):
    with get_connection() as conn:
        cursor = conn.cursor()
            
        cursor.execute("""
            UPDATE users
            SET secret_code = NULL
            WHERE user_id = ?
        """, (staff_id , ))
        conn.commit()

def not_adding_staff(staff_id):
    with get_connection() as conn:
        cursor = conn.cursor()
            
        cursor.execute("""
            UPDATE users
            SET secret_code = ?
            WHERE user_id = ?
        """, (None , staff_id))
        conn.commit()


def retention(user_id , amount):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET balance = balance - ?
            WHERE user_id = ?        
        """, (amount , user_id ))
        
        cursor.execute("""
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = 1  
        """, (amount , ))
        conn.commit()


def transfer(user_id , amount):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?        
        """, (amount , user_id ))
        
        cursor.execute("""
            UPDATE users
            SET balance = balance - ?
            WHERE user_id = 1  
        """, (amount , ))
        conn.commit()



def topup(user_id , amount):
     with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?        
        """, (amount , user_id ))
        
        conn.commit()


def withdraw(user_id, amount):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
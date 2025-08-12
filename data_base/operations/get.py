import sqlite3
from typing import Union , Optional
import logging
from data_base.core import get_connection , logger


def student_data(user_id: int) -> dict:
    """возвращает основную инфорацию про исполнителя"""

    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    name , 
                    rating_sum , 
                    rating_number , 
                    balance , 
                    (SELECT COUNT(*) FROM applications
                    WHERE student_id = ? AND status = 'finish') AS finish_task_count
                FROM users 
                WHERE user_id = ?
            """ , (user_id , user_id))

            result = cursor.fetchone()
            return dict(result) if result else None
    except Exception as e:
        logger.error(f'Error in get.student_data: {e}')


def employer_data(user_id: int) -> dict:
    """возвращает основную инфорацию про исполнителя"""

    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    name , 
                    rating_sum , 
                    rating_number , 
                    balance , 
                    (SELECT COUNT(*) FROM users
                    WHERE secret_code = u.secret_code) AS staff_count , 
                    (SELECT COUNT(*) FROM jobs
                    WHERE employer_id = ?) AS jobs_count , 
                    secret_code
                FROM users u
                WHERE user_id = ?
            """ , (user_id , user_id))

            result = cursor.fetchone()
            return dict(result) if result else None
    except Exception as e:
        logger.error(f'Error in get.employer_data: {e}')


def user_info(user_id: int , column: str) -> Union[str , int]:
    """Возвращает определённое поле пользователя"""

    ALLOWED_COLUMNS = ['user_name' , 'name' , 'rating_sum' , 'rating_number' , 'secret_code' , 'role' , 'created_at' , 'balance']
    
    try:
        if column not in ALLOWED_COLUMNS:
            raise ValueError(f'Invalid column name: {column}')
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column} FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            return result[0] if result else None
    except Exception as e:
        logger.error(f'Error in get.user_info: {e}')


def staff(secret_code):
    """Возвращает список словарей с id_user и name для пользователей с данным секретным ключом"""

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, name
                FROM users
                WHERE secret_code = ?;
            """, (secret_code,))
            
            rows = cursor.fetchall()
            result = [{'user_id': row[0], 'name': row[1]} for row in rows]
            return result
    
    except Exception as e:
        logger.error(f'Error in get.staff: {e}')
        return []


def job_ids_employer(employer_id: int) -> list[int]:
    """Возвращает список ID проектов заказчика."""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT job_id FROM jobs WHERE status != 'canceled' and status != 'completed' and employer_id = ?",
                (employer_id,)
            )
            return [row[0] for row in cursor.fetchall()]

    except sqlite3.Error as e:
        logger.error(f"Error in get_projects_id_employer: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get.job_ids_employer: {e}")
        return None


def job_details(job_id: int) -> dict:
    """Возвращает детальную информация о проекте"""
    
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    j.*,
                    u.name as employer_name
                FROM jobs j
                JOIN users u ON j.employer_id = u.user_id
                WHERE j.job_id = ?
                           """ , (job_id , ))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            data = dict(result)
            return data
    except sqlite3.Error as e:
        logger.error(f'Error in get.project_detalis: {e}' , exc_info=True)
        return None


def approved_application_ids(project_id: int) -> Optional[int]:
    """Возвращает ID подтверждённого отклика для указанного проекта"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT app_id FROM applications WHERE app_id = ? and status = 'accepted'",
                (project_id,)
            )
            
            return [row[0] for row in cursor.fetchall()]
        
    except sqlite3.Error as e:
        logger.error(f"Error in get.approved_application_ids: {e}")
        return None


def application_by_job(job_id: int) -> list:
    """Возвращает список из ID откликов на вакансию"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.app_id FROM applications a 
                JOIN jobs j ON j.job_id = a.job_id 
                WHERE j.job_id = ? AND a.status = 'pending'
                """, (job_id,)
            )
            return [row[0] for row in cursor.fetchall()]
        
    except Exception as e:
        logger.error(f'Error in get.application_by_job: {e}')
        return None

def application_details(app_id: int) -> dict: 
    """возвращает детальную информацию об отклике"""
    
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT
                a.app_id , 
                a.job_id ,  
                
                u.user_id , 
                u.user_name , 
                u.name as student_name, 
                u.rating_sum , 
                u.rating_number
            FROM applications a
            LEFT JOIN users u ON a.student_id = u.user_id
            WHERE a.app_id = ?
            """ , (app_id , ))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            data = dict(result)
            return data
    except Exception as e:
        logger.error(f'Error in get.application_details: {e}')


def job_ids():
    """получаем список всех доступных вакансий"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_id 
                FROM jobs
                WHERE status = 'open'
            """)

            return [row[0] for row in cursor.fetchall()]
    
    except Exception as e:
        logger.error in (f'Error in get.job_ids: {e}')


def applications_student(student_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT a.app_id
                FROM applications a
                JOIN jobs j ON a.job_id = j.job_id
                WHERE a.student_id = ?
                  AND (a.status IN ('accepted' , 'start' , 'finish' , 'done'))
            """, (student_id,))
            
            return [row[0] for row in cursor.fetchall()]
            
    except Exception as e:
        logger.error(f'Error in get.job_ids_student: {e}')
        return None



def job_ids_student(student_id):
    """Возвращает список ID проектов, которые выполняет студент"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT a.job_id
                FROM applications a
                JOIN jobs j ON a.job_id = j.job_id
                WHERE a.student_id = ?
                  AND (a.status IN ('accepted' , 'start' , 'finish' , 'done'))
            """, (student_id,))
            
            return [row[0] for row in cursor.fetchall()]
            
    except Exception as e:
        logger.error(f'Error in get.job_ids_student: {e}')
        return None


def application_info(app_id , column):
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT {column} FROM applications WHERE app_id = ?", (app_id,))
        result = cursor.fetchone()

        return result[0] if result else None


def job_info(job_id: int , column):
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT {column} FROM jobs WHERE job_id = ?" , (job_id , ))
        result = cursor.fetchone()
        
        return result[0] if result else None
    
    
def app_ids_finish(job_id):

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT app_id
                FROM applications
                WHERE status = 'finish' AND job_id = ?
            """, (job_id,))
            
            finished_students = [row[0] for row in cursor.fetchall()]
            
            return finished_students
    
    except Exception as e:
        logger.error(f'Error in student_ids_finish: {e}')
        
        
def staff_secret_code(staff_id: int) -> bool:
     with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT secret_code FROM users WHERE user_id = ?" , (staff_id , ))
        result = cursor.fetchone()
        
        return result[0] if result else None


def staff_data(user_id: int) -> dict:
    """Возвращает основную информацию о сотруднике и его компании"""

    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    staff.name AS staff_name,
                    employer.name AS company_name,
                    ROUND(CAST(employer.rating_sum AS REAL) / employer.rating_number, 1) AS rating,
                    (SELECT COUNT(*) FROM jobs
                     WHERE employer_id = employer.user_id
                       AND status IN ('open', 'in_progress', 'wait')
                       AND staff = ?) AS jobs_count
                FROM users AS staff
                JOIN users AS employer ON staff.secret_code = employer.secret_code AND employer.role = 'employer'
                WHERE staff.user_id = ? AND staff.role = 'staff'
            """, (user_id,user_id))

            result = cursor.fetchone()
            return dict(result) if result else None
    except Exception as e:
        logger.error(f'Error in get.staff_data: {e}')
        return None
    
def add_staff(user_id):
    
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT secret_code FROM users WHERE user_id = ?
            """ , (user_id , ))
            
            secret_code = cursor.fetchall()[0][0]
            
            cursor.execute("""
                SELECT user_id FROM users
                    WHERE secret_code = ?
            """ , (f'!{secret_code}' ,))
            
            result = [row[0] for row in cursor.fetchall()]
            return result
    
    except Exception as e:
        logger.error(f'Error in add_staff: {e}' , exc_info=True)


def my_staff(user_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT secret_code FROM users WHERE user_id = ?
            """, (user_id,))
            secret_code = cursor.fetchone()[0]  # более безопасно

            cursor.execute("""
                SELECT user_id FROM users
                WHERE secret_code = ?
            """, (secret_code,))
            all_ids = [row[0] for row in cursor.fetchall()]
            result = [uid for uid in all_ids if uid != user_id]

            return result

    except Exception as e:
        logger.error(f'Error in my_staff: {e}', exc_info=True)



def staff_job (staff_id):
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT job_id FROM jobs
                       WHERE status != 'canceled' AND status != 'Completed'
                       AND staff = ?
            """, (staff_id , ))
    
        result = [row[0] for row in cursor.fetchall()]
        return result
    
    except Exception as e:
        logger.error(f'Error in staff_job: {e}')
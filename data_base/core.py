import sqlite3
import logging
from pathlib import Path
from config import DATABASE_PATH
from typing import Union

logger = logging.getLogger(__name__)


def get_connection():
    """Возвращает созданное подключение к базе данных"""
    return sqlite3.connect(DATABASE_PATH)



def init_db():
    """Инициализация структуры базы данных"""

    with get_connection() as conn:
        cursor = conn.cursor()
        
        # таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY , 
            user_name TEXT , 
            name TEXT , 
            rating_sum INTEGER DEFAULT 5 , 
            rating_number INTEGER DEFAULT 1 , 
            balance REAL DEFAULT 0 , 
            secret_code TEXT , 
            role TEXT CHECK (role IN ('student' , 'employer' , 'staff' , 'moderator' , 'admin')) , 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
        """)
        
        # таблица вакансий
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT , 
            employer_id INTEGER NOT NULL , 
            title TEXT NOT NULL , 
            description TEXT , 
            date TEXT , 
            start_time TEXT , 
            finish_time TEXT , 
            price REAL , 
            people INTEGER DEFAULT 1 , 
            staff INTEGER , 
            status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open' , 'in_progress' , 'wait' , 'done' , 'completed' , 'canceled')) , 
            edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP , 
            
            FOREIGN KEY (employer_id) REFERENCES users(user_id) , 
            FOREIGN KEY (staff) REFERENCES users(user_id)
        )
        """)
        
        # таблица откликов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            app_id INTEGER PRIMARY KEY AUTOINCREMENT , 
            job_id INTEGER NOT NULL ,
            student_id INTEGER NOT NULL , 
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending' , 'accepted' , 'start' , 'finish' , 'done' , 'completed' , 'canceled')) , 
            start TEXT , 
            finish TEXT , 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP , 
            
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) , 
            FOREIGN KEY (student_id) REFERENCES users(user_id)
        )
        """)
        
        # таблица тех. поддержки
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT ,
            user_id INTEGER NOT NULL ,
            message TEXT NOT NULL ,
            status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open' , 'in_progress' , 'resolved')) ,
            admin_id INTEGER ,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
            resolved_at TIMESTAMP ,
            
            FOREIGN KEY (user_id) REFERENCES users(user_id) ,
            FOREIGN KEY (admin_id) REFERENCES users(user_id)
        )
        """)
        
        cursor.execute("""
            INSERT INTO users (user_id , user_name , name , balance)
            SELECT 1 , 'helper_bot' , 'helper' , 0
            WHERE NOT EXISTS (
                SELECT 1 FROM users WHERE user_id = 1
            )
        """)


def user_exists(user_id: int) -> bool:
    """Проверяет, есть ли пользователь в базе данных с таким ID"""
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?" , (user_id , ))
        
        return cursor.fetchone() is not None
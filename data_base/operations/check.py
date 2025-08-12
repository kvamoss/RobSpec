import sqlite3
from typing import Union
import logging
from data_base.core import get_connection , logger

def is_secret_code_exists(secret_code: str) -> bool:
    """Проверяет, существует ли такой секретный код в базе"""

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM users 
                WHERE secret_code = ? 
                LIMIT 1
            """, (secret_code,))
            result = cursor.fetchone()
            return result[0] > 0 if result else False
        
    except Exception as e:
        logger.error(f'Error in is_secret_code_exists: {e}')
        return False

from .admin import register_admin
from .employer import register_employer
from .general import register_general
from .student import register_student
from .staff import register_staff
from .mod import register_mod

def register_all(bot):
    """Регестрирует все обработчики бота"""
    register_student(bot)
    register_admin(bot)
    register_employer(bot)
    register_general(bot)
    register_staff(bot)
    register_mod(bot)
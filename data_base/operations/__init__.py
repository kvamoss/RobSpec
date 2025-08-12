from .add import user , job , application
from .get import (student_data , employer_data , user_info , staff , job_ids_employer , 
                job_details , approved_application_ids , application_by_job , application_details ,
                job_ids , job_ids_student , application_info , job_info , app_ids_finish, staff_secret_code, 
                staff_data, add_staff , my_staff , staff_job , applications_student)
from .check import is_secret_code_exists
from .updata import (approv_application , disapprov_application , start_jobs , finish_jobs , 
                    user_rating , job_confirm, join_employer , adding_staff , not_adding_staff, 
                    retention , transfer , topup , withdraw , application_confirm , remove_staff)

class addOperations:
    user = user
    job = job
    application = application

class getOperations:
    student_data = student_data
    employer_data = employer_data
    user_info = user_info
    staff = staff
    job_ids_employer = job_ids_employer
    job_details = job_details
    approved_application_ids = approved_application_ids
    application_by_job = application_by_job
    application_details = application_details
    job_ids = job_ids
    job_ids_student = job_ids_student
    application_info = application_info
    job_info = job_info
    app_ids_finish = app_ids_finish
    staff_secret_code = staff_secret_code
    staff_data = staff_data
    my_staff = my_staff
    add_staff = add_staff
    staff_job = staff_job
    applications_student = applications_student

class checkOperations:
    is_secret_code_exists = is_secret_code_exists

class updata:
    approv_application = approv_application
    disapprov_application = disapprov_application
    start_jobs = start_jobs
    finish_jobs = finish_jobs
    user_rating = user_rating
    job_confirm = job_confirm
    join_employer = join_employer
    adding_staff = adding_staff
    not_adding_staff = not_adding_staff
    retention = retention
    transfer = transfer
    topup = topup
    withdraw = withdraw
    application_confirm = application_confirm
    remove_staff = remove_staff

add = addOperations
get = getOperations
check = checkOperations
updata = updata
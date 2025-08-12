import os
from dotenv import load_dotenv

load_dotenv('./.gitignore!/.env')

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = "data_base/RobSpec.db"
chat_mod = '-1002777746914'
commission_rate = 0.05

owners = ['']
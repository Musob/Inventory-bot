import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# MySQL sozlamalari (Alwaysdata)
DB_HOST = os.getenv("DB_HOST", "mysql-[account].alwaysdata.net")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "[account]")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "[account]_inventory")

DATABASE_URL = (
    f"mysql+asyncmy://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Adminlar ro'yxati (ixtiyoriy)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
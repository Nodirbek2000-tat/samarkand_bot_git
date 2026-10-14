from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot token
ADMINS = env.list("ADMINS", default=[])  # adminlar ro'yxati (bot ishga tushganda xabar oladi)
IP = env.str("ip", default="localhost")  # Xosting ip manzili

# Sayt (Django) bilan aloqa — ../samarkand
API_URL = env.str("API_URL", default="http://127.0.0.1:8000/api").rstrip("/")
API_SECRET = env.str("BOT_API_SECRET")  # Django .env dagi BOT_API_SECRET bilan AYNAN bir xil bo'lishi kerak
SITE_URL = env.str("SITE_URL", default="http://localhost:3000").rstrip("/")
OUTBOX_INTERVAL = env.float("OUTBOX_INTERVAL", default=3.0)  # navbatdagi xabarlarni necha soniyada tekshirish

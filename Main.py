import os
import logging
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ⚙️ КОНФІГУРАЦІЯ (беремо з налаштувань Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "956876109"))

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (щоб сервіс не падав) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health server started on port {port}")
    server.serve_forever()

# --- ЛОГІКА БОТА ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🏠 Оренда"), KeyboardButton("💰 Купівля")],
        [KeyboardButton("📊 Продаж"), KeyboardButton("🗺 Райони Києва")],
        [KeyboardButton("⚠️ Ризики"), KeyboardButton("❓ Допомога")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "👋 Вітаю! Я твій AI-ріелтор у Києві. Оберіть розділ нижче 👇"
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    responses = {
        "🏠 Оренда": "🏠 Оренда: ціни у 2026 році стартують від 10,000 грн за 1-к квартиру.",
        "💰 Купівля": "💰 Купівля: новобудови від $1,400/м². Рекомендую LUN.ua.",
        "📊 Продаж": "📊 Продаж: підготуйте документи та зробіть якісні фото.",
        "🗺 Райони Києва": "🗺 Печерськ — престиж, Поділ — історія, Оболонь — затишок.",
        "⚠️ Ризики": "⚠️ Ніколи не скидайте передоплату до огляду квартири!",
        "❓ Допомога": "Напишіть своє питання, і я (або адмін) відповім вам."
    }
    reply = responses.get(text, "Оберіть варіант з меню.")
    await update.message.reply_text(reply)

# --- ЗАПУСК ---
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не знайдено в змінних середовища!")
        return

    # Запуск веб-сервера в окремому потоці
    threading.Thread(target=run_health_server, daemon=True).start()

    # Створення бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))
    
    logger.info("🤖 Бот запущений!")
    application.run_polling()

if __name__ == '__main__':
    main()
  

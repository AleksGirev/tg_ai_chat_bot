import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🟢 Команда /start от {update.effective_user.username}")
    await update.message.reply_text("Бот работает! Тест 1/3 ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📩 Сообщение: {update.message.text}")
    await update.message.reply_text(f"Получил: {update.message.text}")

def main():
    print("🚀 Запуск бота...")
    token = os.getenv("TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TOKEN или TELEGRAM_BOT_TOKEN не установлен в переменных окружения")
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("🤖 Бот запущен. Идите в Telegram и напишите /start")
    app.run_polling()

if __name__ == '__main__':
    main()
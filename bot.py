"""
Telegram бот, который соглашается с пользователем
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот, который полностью согласен с тобой. "
        "Просто отправь мне любое сообщение, и я отвечу, что полностью с тобой согласен."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "Просто отправь любое сообщение, и я отвечу, что полностью с тобой согласен."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    # Просто отвечаем, что согласны
    await update.message.reply_text("полностью с тобой согласен")


def main():
    """Основная функция для запуска бота"""
    # Получаем токен бота из переменной окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN не установлен. "
            "Пожалуйста, установите токен бота в переменной окружения."
        )
    
    # Создаем приложение
    application = Application.builder().token(bot_token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


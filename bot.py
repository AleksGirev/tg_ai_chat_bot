"""
Telegram бот для общения с LLM через API
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from llm_client import LLMClient

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация клиента LLM
llm_client = LLMClient()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот, который может общаться с вами через LLM. "
        "Просто отправьте мне сообщение, и я передам его в LLM и отправлю вам ответ."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "Просто отправьте любое сообщение, и я передам его в LLM."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_message = update.message.text
    
    # Отправляем сообщение о том, что бот думает
    thinking_message = await update.message.reply_text("Думаю...")
    
    try:
        # Получаем ответ от LLM
        llm_response = await llm_client.get_response(user_message)
        
        # Удаляем сообщение "Думаю..." и отправляем ответ
        await thinking_message.delete()
        await update.message.reply_text(llm_response)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await thinking_message.delete()
        await update.message.reply_text(
            f"Извините, произошла ошибка при обработке вашего запроса: {str(e)}"
        )


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


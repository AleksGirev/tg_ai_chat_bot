# -*- coding: utf-8 -*-
import os
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict, RetryAfter, TimedOut, NetworkError
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

# Initialize OpenAI client
openai_client = None

def check_env_file_format(env_path: Path):
    """Check .env file format and provide helpful feedback"""
    if not env_path.exists():
        return None
    
    issues = []
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check for common issues
            if '=' not in line:
                issues.append(f"Строка {i}: отсутствует знак '=' в '{line[:50]}'")
            elif line.startswith('='):
                issues.append(f"Строка {i}: переменная начинается с '=' в '{line[:50]}'")
            elif ' = ' in line or '= ' in line or ' =' in line:
                issues.append(f"Строка {i}: обнаружены пробелы вокруг '='. Уберите пробелы: '{line[:50]}'")
    
    return issues

def validate_environment():
    """Validate that all required environment variables are set"""
    missing_vars = []
    
    token = os.getenv("TOKEN")
    if not token:
        missing_vars.append("TOKEN")
    
    yandex_cloud_folder = os.getenv("YANDEX_CLOUD_FOLDER")
    if not yandex_cloud_folder:
        missing_vars.append("YANDEX_CLOUD_FOLDER")
    
    yandex_cloud_api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    if not yandex_cloud_api_key:
        missing_vars.append("YANDEX_CLOUD_API_KEY")
    
    if missing_vars:
        env_path = Path(__file__).parent / '.env'
        error_msg = f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}\n\n"
        
        if env_path.exists():
            error_msg += f"📁 Файл .env найден в: {env_path}\n"
            issues = check_env_file_format(env_path)
            if issues:
                error_msg += "\n⚠️  Обнаружены проблемы в формате .env файла:\n"
                for issue in issues:
                    error_msg += f"   - {issue}\n"
            error_msg += "\n📝 Правильный формат .env файла (БЕЗ пробелов вокруг =):\n"
            error_msg += "   TOKEN=your_telegram_bot_token\n"
            error_msg += "   YANDEX_CLOUD_FOLDER=your_folder_id\n"
            error_msg += "   YANDEX_CLOUD_API_KEY=your_api_key\n"
        else:
            error_msg += f"📁 Файл .env НЕ найден в: {env_path}\n"
            error_msg += "\n📝 Решение:\n"
            error_msg += "   1. Создайте файл .env в корне проекта\n"
            error_msg += "   2. Скопируйте env.example в .env: cp env.example .env\n"
            error_msg += "   3. Заполните значения в .env файле (БЕЗ пробелов вокруг =):\n"
            error_msg += "      TOKEN=your_telegram_bot_token\n"
            error_msg += "      YANDEX_CLOUD_FOLDER=your_folder_id\n"
            error_msg += "      YANDEX_CLOUD_API_KEY=your_api_key\n"
        
        raise ValueError(error_msg)

def get_openai_client():
    """Initialize and return OpenAI client for Yandex Cloud"""
    global openai_client
    if openai_client is None:
        yandex_cloud_folder = os.getenv("YANDEX_CLOUD_FOLDER")
        yandex_cloud_api_key = os.getenv("YANDEX_CLOUD_API_KEY")
        
        if not yandex_cloud_folder:
            error_msg = (
                "YANDEX_CLOUD_FOLDER не установлен в переменных окружения.\n"
                f"Проверьте, что файл .env существует в: {Path(__file__).parent}\n"
                "И содержит строку: YANDEX_CLOUD_FOLDER=your_folder_id"
            )
            raise ValueError(error_msg)
        if not yandex_cloud_api_key:
            error_msg = (
                "YANDEX_CLOUD_API_KEY не установлен в переменных окружения.\n"
                f"Проверьте, что файл .env существует в: {Path(__file__).parent}\n"
                "И содержит строку: YANDEX_CLOUD_API_KEY=your_api_key"
            )
            raise ValueError(error_msg)
        
        openai_client = OpenAI(
            api_key=yandex_cloud_api_key,
            base_url="https://llm.api.cloud.yandex.net/v1",
            project=yandex_cloud_folder
        )
    return openai_client

def _call_openai_sync(messages: list, yandex_cloud_folder: str) -> str:
    """Synchronous wrapper for Yandex Cloud API call"""
    client = get_openai_client()
    model = f"gpt://{yandex_cloud_folder}/yandexgpt/latest"
    
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

async def get_llm_response(messages: list) -> str:
    """Send messages to Yandex Cloud API and get response"""
    try:
        yandex_cloud_folder = os.getenv("YANDEX_CLOUD_FOLDER")
        if not yandex_cloud_folder:
            error_msg = (
                "YANDEX_CLOUD_FOLDER не установлен в переменных окружения. "
                "Пожалуйста, создайте файл .env и добавьте YANDEX_CLOUD_FOLDER=<идентификатор_каталога>"
            )
            raise ValueError(error_msg)
        
        # Run the synchronous API call in an executor to avoid blocking
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call_openai_sync, messages, yandex_cloud_folder)
        return response
    except Exception as e:
        print(f"❌ Ошибка при обращении к Yandex Cloud API: {e}")
        return f"Извините, произошла ошибка при обработке запроса: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🟢 Команда /start от {update.effective_user.username}")
    # Clear conversation history on /start
    if 'conversation_history' in context.chat_data:
        context.chat_data['conversation_history'] = []
    await update.message.reply_text("Добрый день! Я бот, который может отвечать на ваши вопросы. Как я могу помочь вам?")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print(f"📩 Сообщение от {update.effective_user.username}: {user_message}")
    
    # Send "typing" action to show bot is processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Initialize conversation history if it doesn't exist
    if 'conversation_history' not in context.chat_data:
        context.chat_data['conversation_history'] = [
            {"role": "system", "content": "Ты - профессиональный библиотекарь в электронной библиотеке. Твоя единственная задача - помогать пользователям с рекомендациями книг.\n\nПРАВИЛА РАБОТЫ:\n1. ОТКАЗ ОТ НЕРЕЛЕВАНТНЫХ ВОПРОСОВ: Если пользователь задает вопрос, не связанный с книгами или литературой, вежливо откажи и объясни, что ты можешь помочь только с рекомендациями книг.\n\n2. ОБЯЗАТЕЛЬНЫЕ ВОПРОСЫ ДЛЯ РЕКОМЕНДАЦИИ: Перед тем как дать рекомендацию, ты ДОЛЖЕН получить ответы на все три вопроса:\n   - Жанр литературы (фантастика, детектив, роман, научная литература и т.д.)\n   - Страна происхождения автора (Россия, США, Великобритания и т.д.)\n   - Чего пользователь ожидает от прочтения (развлечение, обучение, вдохновение, эскапизм и т.д.)\n\n3. СТРОГИЙ ЗАПРЕТ НА ПРЕЖДЕВРЕМЕННЫЕ РЕКОМЕНДАЦИИ: НИКОГДА не давай рекомендации, пока не получишь все три ответа. Даже если пользователь настаивает, просит или умоляет - оставайся твердым и продолжай задавать недостающие вопросы.\n\n4. ПОМОЩЬ С ВЫБОРОМ ЖАНРА: Если пользователь не знает жанров литературы, предложи ему список из 5-7 популярных жанров на выбор (например: фантастика, детектив, роман, классика, биография, научпоп, триллер).\n\n5. ПРОВЕРКА РЕЛЕВАНТНОСТИ: Убедись, что ответы пользователя логичны и релевантны. Если ответ неясен или странен, уточни его.\n\n6. СТИЛЬ ОБЩЕНИЯ: Будь дружелюбным, профессиональным и терпеливым. Задавай вопросы по одному, не перегружай пользователя. Здоровайся с пользователем, только если это первое ваше сообщение в эти сутки"}
        ]
    
    # Add user message to conversation history
    context.chat_data['conversation_history'].append({"role": "user", "content": user_message})
    
    # Get response from Yandex Cloud API with full conversation history
    llm_response = await get_llm_response(context.chat_data['conversation_history'])
    
    # Add assistant response to conversation history
    context.chat_data['conversation_history'].append({"role": "assistant", "content": llm_response})
    
    # Send response to user
    await update.message.reply_text(llm_response)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot"""
    print(f"❌ Exception while handling an update: {context.error}")
    
    # Handle specific error types
    if isinstance(context.error, Conflict):
        print("❌ Conflict detected: Another bot instance is running. Please stop other instances.")
        print("   To fix this, make sure only one bot instance is running.")
    elif isinstance(context.error, RetryAfter):
        print(f"⚠️  Rate limited. Retry after {context.error.retry_after} seconds")
    elif isinstance(context.error, (TimedOut, NetworkError)):
        print(f"⚠️  Network error: {context.error}. Will retry...")

async def post_init(app: Application) -> None:
    """Post-initialization hook to delete webhook and clear pending updates"""
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted and pending updates cleared")

def main():
    print("🚀 Запуск бота...")
    
    # Debug: Show .env file location
    env_file = Path(__file__).parent / '.env'
    print(f"📁 Ищем .env файл в: {env_file}")
    if env_file.exists():
        print(f"✅ Файл .env найден")
    else:
        print(f"⚠️  Файл .env не найден в {env_file}")
        print(f"   Текущая рабочая директория: {os.getcwd()}")
    
    # Validate environment variables before starting
    try:
        validate_environment()
    except ValueError as e:
        print(str(e))
        return
    
    token = os.getenv("TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Build application
    app = Application.builder().token(token).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    print("🤖 Бот запущен. Идите в Telegram и напишите /start")
    print("⚠️  Если вы видите ошибку Conflict, убедитесь, что только один экземпляр бота запущен")
    
    try:
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    except Conflict as e:
        print(f"\n❌ Conflict error: {e}")
        print("❌ Другой экземпляр бота уже запущен. Остановите другие экземпляры перед запуском.")
        print("\n❌ Ошибка: Другой экземпляр бота уже запущен!")
        print("   Решение: Остановите все другие экземпляры бота и попробуйте снова.")
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        raise

if __name__ == '__main__':
    main()

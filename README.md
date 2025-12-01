# Telegram бот с интеграцией LLM

Этот бот принимает сообщения от пользователей Telegram, отправляет их в публичную LLM через API и возвращает ответ пользователю.

## Возможности

- ✅ Прием сообщений от пользователей Telegram
- ✅ Интеграция с публичными LLM API (OpenAI, Anthropic, кастомные API)
- ✅ Асинхронная обработка запросов
- ✅ Обработка ошибок
- ✅ Поддержка команд /start и /help

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте Telegram бота:
   - Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
   - Отправьте команду `/newbot`
   - Следуйте инструкциям и получите токен бота

3. Настройте переменные окружения:
   - Скопируйте `env.example` в `.env` (или установите переменные окружения напрямую)
   - Заполните необходимые переменные:
     - `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
     - `LLM_API_KEY` - API ключ для LLM (OpenAI, Anthropic и т.д.)
     - `LLM_PROVIDER` - провайдер LLM (openai, anthropic, custom)
     - `LLM_MODEL` - модель для использования
     - `LLM_API_URL` - URL API (для OpenAI можно оставить по умолчанию)

## Использование

### Запуск с переменными окружения

```bash
export TELEGRAM_BOT_TOKEN="your_token"
export LLM_API_KEY="your_api_key"
export LLM_PROVIDER="openai"
python bot.py
```

### Запуск с .env файлом

Если вы используете библиотеку `python-dotenv`, можно создать `.env` файл и загружать переменные из него:

```bash
pip install python-dotenv
```

Затем добавьте в начало `bot.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Поддерживаемые LLM провайдеры

### OpenAI
```bash
export LLM_PROVIDER=openai
export LLM_API_KEY=sk-...
export LLM_MODEL=gpt-3.5-turbo
```

### Anthropic (Claude)
```bash
export LLM_PROVIDER=anthropic
export LLM_API_KEY=sk-ant-...
export LLM_MODEL=claude-3-sonnet-20240229
```

### Кастомный API
```bash
export LLM_PROVIDER=custom
export LLM_API_KEY=your_key
export LLM_API_URL=https://your-api.com/v1/chat
export LLM_MODEL=your-model
```

Для кастомного API может потребоваться доработка метода `_get_custom_response` в `llm_client.py` под структуру вашего API.

## Структура проекта

```
telegram-bot/
├── bot.py              # Основной файл бота
├── llm_client.py       # Клиент для работы с LLM API
├── requirements.txt    # Зависимости Python
├── env.example         # Пример файла с переменными окружения
├── .gitignore          # Игнорируемые файлы для Git
└── README.md           # Документация
```

## Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку

Любое текстовое сообщение будет отправлено в LLM, и бот вернет ответ.

## Разработка

Для разработки рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Лицензия

Этот проект создан для образовательных целей.


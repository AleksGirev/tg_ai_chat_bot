#!/bin/bash

# Скрипт для запуска Telegram бота
cd "$(dirname "$0")"

# Проверка наличия переменных окружения
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Ошибка: TELEGRAM_BOT_TOKEN не установлен"
    echo "Пожалуйста, установите переменные окружения перед запуском"
    echo "Пример:"
    echo "  export TELEGRAM_BOT_TOKEN='your_token'"
    echo "  export LLM_API_KEY='your_api_key'"
    echo "  export LLM_PROVIDER='openai'"
    exit 1
fi

# Запуск бота
echo "Запуск Telegram бота..."
python3 bot.py


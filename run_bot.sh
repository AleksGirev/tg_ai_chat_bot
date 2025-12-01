#!/bin/bash

# Скрипт для запуска Telegram бота
cd "$(dirname "$0")"

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден"
    echo "📝 Создайте файл .env на основе env.example:"
    echo "   cp env.example .env"
    echo ""
    echo "Затем заполните следующие переменные в .env:"
    echo "   - YANDEX_CLOUD_FOLDER=<идентификатор_каталога>"
    echo "   - YANDEX_CLOUD_API_KEY=<значение_API-ключа>"
    echo "   - TOKEN=<ваш_telegram_токен>"
    exit 1
fi

# Запуск бота
echo "Запуск Telegram бота..."
python3 llm_client.py


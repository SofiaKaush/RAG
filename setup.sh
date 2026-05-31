#!/bin/bash
# Quick Start Script for RAG Application

set -e

echo "🚀 RAG Application - Быстрый старт"
echo "=================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

echo "✓ Python3 найден"

# Проверка зависимостей
echo ""
echo "📦 Установка зависимостей..."
pip install -q -r requirements.txt
echo "✓ Зависимости установлены"

# Создание директорий
echo ""
echo "📁 Создание директорий..."
mkdir -p chroma_db
echo "✓ Директории готовы"

# Копирование .env
if [ ! -f .env ]; then
    echo ""
    echo "⚙️ Создание конфига из примера..."
    cp .env.example .env
    echo "✓ .env создан (отредактируйте при необходимости)"
fi

# Информация
echo ""
echo "✨ Все готово!"
echo ""
echo "📝 Перед запуском:"
echo "1. Убедитесь, что LM Studio запущена на localhost:1234"
echo "2. Загрузите модель в LM Studio"
echo "3. Запустите приложение: python app.py"
echo ""
echo "🌐 Приложение будет доступно на: http://localhost:5011"
echo ""

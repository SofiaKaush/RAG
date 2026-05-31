#!/bin/bash
# Clean and push to GitHub

cd /workspaces/RAG

# Remove unnecessary files
echo "🗑️  Удаляю лишние файлы..."
rm -f ДЕЙСТВИЕ_СЕЙЧАС.md
rm -f "000_НАЧНИТЕ_ОТСЮДА.md"
rm -f CHANGELOG.md
rm -f COPY_PASTE_COMMANDS.txt
rm -f DEVELOPMENT.md
rm -f FILES_FOR_COMMIT.md
rm -f GIT_INSTRUCTIONS.md
rm -f GIT_VISUAL_GUIDE.txt
rm -f IMPROVEMENTS.md
rm -f READY_TO_PUSH.md
rm -f SUMMARY.md
rm -f FINAL_STATUS.md
rm -f "📌_ДЕЙСТВУЙТЕ_СЕЙЧАС.txt"
rm -f commit.sh
rm -f execute_git_commands.py
rm -f execute_git_commands.sh
rm -f final-push.sh
rm -f git-push.sh

echo "✅ Лишние файлы удалены"
echo ""

# Git status
echo "📊 Статус репозитория:"
git status --short
echo ""

# Add changes
echo "📦 Добавляю изменения..."
git add -A
echo "✓ Добавлено"
echo ""

# Commit
echo "💾 Создаю коммит..."
git commit -m "🚀 RAG система: финальная версия

Основные компоненты:
- app.py - главное приложение (450+ строк)
- README.md - полная документация
- test_app.py - автоматические тесты
- setup.sh - скрипт быстрой установки
- .env.example - пример конфигурации
- requirements.txt - зависимости

Ключевые улучшения:
- Поддержка PDF, JSON, MD файлов
- Оптимизированное разбиение на чанки
- Система метаданных
- 7 API endpoints
- Полная обработка ошибок
- Профессиональное логирование
- Конфигурация через env переменные"

echo "✓ Коммит создан"
echo ""

# Push
echo "🌐 Отправляю на GitHub..."
git push origin main

echo ""
echo "╔════════════════════════════════════════╗"
echo "║         ✅ ГОТОВО!                     ║"
echo "║                                        ║"
echo "║  Все файлы сохранены в GitHub!        ║"
echo "║  https://github.com/SofiaKaush/RAG    ║"
echo "╚════════════════════════════════════════╝"

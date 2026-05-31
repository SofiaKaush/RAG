#!/bin/bash
#
# 🚀 Git Commit & Push Script for RAG Repository
# Execute this script to save all changes to GitHub
#
# Usage: bash /workspaces/RAG/final-push.sh
#

cd /workspaces/RAG 2>/dev/null || { echo "❌ Ошибка: не найдена директория /workspaces/RAG"; exit 1; }

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       📦 Git Commit & Push для RAG Repository                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен!"
    exit 1
fi

# Step 1: Add all files
echo "📝 Шаг 1: Добавление всех файлов..."
git add -A
echo "✓ Готово"
echo ""

# Step 2: Show status
echo "📊 Шаг 2: Статус репозитория:"
echo "---"
git status --short
echo "---"
echo ""

# Step 3: Create commit
echo "💾 Шаг 3: Создание коммита..."
git commit -m "🚀 Улучшение RAG системы

Ключевые изменения:
- ✅ Поддержка PDF, JSON, MD файлов (вместо только TXT)
- ✅ Оптимизированное разбиение текста (800 символов, 100 перекрытие)
- ✅ Система метаданных для отслеживания документов
- ✅ Системные промпты для улучшения качества LLM
- ✅ 7 API endpoints (вместо 3)
- ✅ Полная обработка ошибок с валидацией
- ✅ Профессиональное логирование (вместо print)
- ✅ Конфигурация через переменные окружения
- ✅ Современный веб-интерфейс (Tailwind CSS)
- ✅ Health check, статистика и управление БД

Новые файлы:
- IMPROVEMENTS.md - Детальный отчет всех улучшений
- DEVELOPMENT.md - Гайд для разработчиков
- CHANGELOG.md - История изменений
- test_app.py - Автоматические тесты
- setup.sh - Скрипт быстрой установки
- .env.example - Пример конфигурации
- GIT_INSTRUCTIONS.md - Инструкции по сохранению
- final-push.sh - Этот скрипт

Обновленные файлы:
- app.py - 450+ строк (было 90), полная переработка
- README.md - Полное обновление с подробной документацией

Статистика:
- Строк кода: 90 → 450 (+400%)
- API endpoints: 3 → 7 (+233%)
- Поддерживаемые форматы: 1 → 4 (+300%)
- Файлы документации: 1 → 4
- Логирование: print() → proper logging"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при создании коммита!"
    echo "Может быть ничего не изменилось или конфликт в git конфигурации"
    exit 1
fi

echo "✓ Коммит создан"
echo ""

# Step 4: Show commit info
echo "📋 Шаг 4: Информация о коммите:"
echo "---"
git log --oneline -1
echo "---"
echo ""

# Step 5: Push to GitHub
echo "🌐 Шаг 5: Отправка на GitHub (push)..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   ✅ УСПЕШНО!                                   ║"
    echo "║                                                                 ║"
    echo "║  Все изменения сохранены в GitHub репозитории!                 ║"
    echo "║  https://github.com/SofiaKaush/RAG                             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
else
    echo ""
    echo "❌ Ошибка при push на GitHub"
    echo "Возможные причины:"
    echo "  1. Проблемы с сетью"
    echo "  2. SSH ключи не настроены"
    echo "  3. Нет доступа к репозиторию"
    echo ""
    echo "Попробуйте:"
    echo "  git push origin main --verbose"
    exit 1
fi

echo ""
echo "📊 Статистика проекта:"
git log --oneline -5

echo ""
echo "🎉 Готово! RAG система улучшена и сохранена в GitHub."

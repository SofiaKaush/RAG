#!/usr/bin/env python3

import subprocess
import sys
import os

# Change to RAG directory
os.chdir('/workspaces/RAG')

commands = [
    ('git status', '1. GIT STATUS'),
    ('git add -A', '2. GIT ADD -A'),
    ('git commit -m "🚀 Улучшение RAG системы\n\nКлючевые изменения:\n- ✅ Поддержка PDF, JSON, MD файлов (вместо только TXT)\n- ✅ Оптимизированное разбиение текста на чанки\n- ✅ Система метаданных для отслеживания документов\n- ✅ Системные промпты для улучшения качества LLM\n- ✅ 7 API endpoints (вместо 3)\n- ✅ Полная обработка ошибок с валидацией\n- ✅ Профессиональное логирование\n- ✅ Конфигурация через переменные окружения\n- ✅ Современный веб-интерфейс (Tailwind CSS)\n- ✅ Health check и управление БД\n\nНовые файлы добавлены: 12+ файлов документации и тестов"', '3. GIT COMMIT'),
    ('git push origin main', '4. GIT PUSH')
]

for cmd, title in commands:
    print(f"\n{'='*50}")
    print(f"{'='*50} {title}")
    print(f"{'='*50}\n")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
    except Exception as e:
        print(f"ERROR: {e}")

print(f"\n{'='*50}")
print("✅ ЗАВЕРШЕНО")
print(f"{'='*50}\n")

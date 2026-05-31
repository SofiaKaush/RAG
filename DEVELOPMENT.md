# Development Guide for RAG Application

## 🔧 Архитектура

### Компоненты

1. **Frontend** - Веб-интерфейс (HTML + Tailwind CSS + JavaScript)
2. **Backend** - Flask приложение
3. **Vector DB** - ChromaDB для хранения эмбеддингов
4. **Embeddings** - sentence-transformers локально
5. **LLM** - OpenAI compatible API (LM Studio)

## 📊 Поток данных

```
Документ → Извлечение текста → Разбиение на чанки → Эмбеддинги → ChromaDB
                                                            ↓
                                                    Поиск релевантных чанков
                                                            ↓
                                                    Формирование контекста
                                                            ↓
                                                    LLM запрос → Ответ
```

## 🔄 Ключевые улучшения

### 1. Многоформатная поддержка
- ✅ TXT файлы
- ✅ PDF через PyPDF2
- ✅ JSON
- ✅ Markdown

### 2. Оптимизированное разбиение
```python
chunk_size = 800 символов
overlap = 100 символов (12.5%)
```
Это обеспечивает:
- Контекстность каждого чанка
- Не дублирование информации
- Оптимальное покрытие

### 3. Система метаданных
Каждый чанк содержит:
- `filename` - исходный файл
- `chunk_index` - номер чанка
- `timestamp` - время загрузки

### 4. Улучшенные промпты
- Система prompts для контролируемого поведения
- Контекст-aware ответы
- Обработка ошибок

### 5. API Endpoints
- `/stats` - статистика
- `/clear` - управление БД
- `/health` - мониторинг
- Полная обработка ошибок

## 🧪 Тестирование

```bash
# Запустить тесты
python test_app.py

# Ручной тест загрузки
curl -F "file=@doc.pdf" http://localhost:5011/upload

# Ручной тест вопроса
curl -X POST http://localhost:5011/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Что в документе?"}'
```

## 🚀 Оптимизация производительности

### Для больших документов (>10MB)
1. Уменьшить `CHUNK_SIZE` до 400-600
2. Уменьшить `N_SEARCH_RESULTS` до 3-4
3. Использовать более быструю модель embeddings

### Для улучшения качества
1. Увеличить `N_SEARCH_RESULTS` до 7-10
2. Улучшить систему prompts
3. Использовать более мощную LLM модель

## 🔐 Безопасность

- Валидация входных данных (max 1000 chars для вопроса)
- Обработка исключений на каждом уровне
- Не логирование чувствительной информации
- Изоляция ошибок LLM

## 📈 Мониторинг

Приложение логирует:
- Загрузку моделей
- Обработку документов
- Статистику поиска
- Ошибки и исключения

Пример:
```
✓ Модель эмбеддингов загружена
✓ Chroma DB инициализирована
✓ OpenAI клиент инициализирован
🚀 Запуск RAG приложения на http://0.0.0.0:5011
Загрузка файла: document.pdf
Создание эмбеддингов для 25 чанков...
✓ Загружено 25 чанков из document.pdf
Поиск контекста для: О чем документ?...
Найдено 5 релевантных чанков
✓ Ответ получен успешно
```

## 🔗 Интеграция

### С другими сервисами
```python
from app import collection, EMBED_MODEL

# Прямой доступ к векторной БД
docs = collection.get()

# Использование модели эмбеддингов
embedding = EMBED_MODEL.encode("текст")
```

## 📝 Добавление новых функций

### Пример: Поддержка Word документов

```python
from docx import Document

def extract_text_from_docx(file_obj) -> str:
    doc = Document(file_obj)
    return "\n".join([p.text for p in doc.paragraphs])

# Добавить в extract_text_from_file
elif ext == '.docx':
    return extract_text_from_docx(file_obj)
```

## 🆘 Отладка

### Включить debug режим
```python
# В app.py
app.run(debug=True)
```

### Просмотр логов Chroma
```python
collection.get(include=["metadatas", "documents"])
```

### Тест эмбеддингов
```python
from app import EMBED_MODEL
vec = EMBED_MODEL.encode("тестовый текст")
print(f"Размер вектора: {len(vec)}")
```

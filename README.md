Ultimate RAG App 🚀

Автономное RAG-приложение для анализа документов и кода.

Установка

Установите зависимости:

pip install flask chromadb openai sentence-transformers PyPDF2


Запуск:

python app.py


Особенности

Локальные эмбеддинги: Используется sentence-transformers, сервер LM Studio для векторов больше не нужен.

Гибкость: Поддерживает PDF, TXT, MD и клонирование Git-репозиториев.
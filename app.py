import os
import chromadb
from flask import Flask, request, jsonify, render_template_string, Response
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import PyPDF2

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 5011
app = Flask(__name__)

# Конфигурация
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
N_SEARCH_RESULTS = 5
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "lm-studio")
LLM_MODEL = os.getenv("LLM_MODEL", "local-model")

# Инициализация
try:
    EMBED_MODEL = SentenceTransformer(EMBED_MODEL_NAME)
    logger.info("✓ Модель эмбеддингов загружена")
except Exception as e:
    logger.error(f"✗ Ошибка загрузки модели эмбеддингов: {e}")
    raise

try:
    os.makedirs(CHROMA_DIR, exist_ok=True)
    chroma = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma.get_or_create_collection(
        name="rag_docs",
        metadata={"hnsw:space": "cosine"}
    )
    logger.info("✓ Chroma DB инициализирована")
except Exception as e:
    logger.error(f"✗ Ошибка инициализации Chroma: {e}")
    raise

# Клиент для LLM
try:
    client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
    logger.info("✓ OpenAI клиент инициализирован")
except Exception as e:
    logger.error(f"✗ Ошибка инициализации LLM: {e}")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RAG Ассистент</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-slate-900 to-slate-800 text-white p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl font-bold mb-2 text-blue-400">🤖 RAG Ассистент</h1>
        <p class="text-slate-400 mb-6">Анализ документов с помощью локальной LLM</p>
        
        <!-- Статистика -->
        <div id="stats" class="grid grid-cols-3 gap-4 mb-6">
            <div class="bg-slate-700 p-4 rounded-lg">
                <p class="text-slate-400 text-sm">Загруженные документы</p>
                <p id="docCount" class="text-2xl font-bold">0</p>
            </div>
            <div class="bg-slate-700 p-4 rounded-lg">
                <p class="text-slate-400 text-sm">Чанков в БД</p>
                <p id="chunkCount" class="text-2xl font-bold">0</p>
            </div>
            <div class="bg-slate-700 p-4 rounded-lg">
                <p class="text-slate-400 text-sm">Статус сервера</p>
                <p id="status" class="text-2xl font-bold text-green-400">✓ OK</p>
            </div>
        </div>

        <!-- Загрузка документа -->
        <div class="bg-slate-700 p-6 rounded-xl mb-6 border border-slate-600">
            <h2 class="text-xl font-bold mb-4">📄 Загрузить документ</h2>
            <p class="text-slate-400 text-sm mb-4">Поддерживаемые форматы: TXT, PDF, JSON</p>
            <div class="flex gap-4">
                <input type="file" id="file" accept=".txt,.pdf,.json" class="flex-1 text-sm text-slate-400">
                <button onclick="upload()" class="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded font-semibold transition">
                    Загрузить
                </button>
                <button onclick="clearDB()" class="bg-red-600 hover:bg-red-700 px-6 py-2 rounded font-semibold transition">
                    Очистить БД
                </button>
            </div>
            <div id="uploadStatus" class="mt-2 text-sm"></div>
        </div>

        <!-- Вопросы-ответы -->
        <div class="bg-slate-700 p-6 rounded-xl border border-slate-600">
            <h2 class="text-xl font-bold mb-4">❓ Задайте вопрос</h2>
            <div class="flex gap-2 mb-4">
                <input type="text" id="q" placeholder="Напишите вопрос..." 
                    class="flex-1 p-3 rounded bg-slate-800 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onkeypress="if(event.key==='Enter') ask()">
                <button onclick="ask()" class="bg-green-600 hover:bg-green-700 px-6 py-3 rounded font-semibold transition">
                    🔍 Спросить
                </button>
            </div>
            <div id="loading" class="text-slate-400 text-sm hidden">⏳ Обработка...</div>
            <div id="res" class="mt-4 p-4 bg-slate-900 rounded whitespace-pre-wrap text-sm leading-relaxed hidden"></div>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                const r = await fetch('/stats');
                const d = await r.json();
                document.getElementById('docCount').innerText = d.documents;
                document.getElementById('chunkCount').innerText = d.chunks;
            } catch (e) {
                console.error('Ошибка загрузки статистики:', e);
            }
        }

        async function upload() {
            const f = document.getElementById('file').files[0];
            if (!f) {
                alert('Выберите файл');
                return;
            }
            const fd = new FormData();
            fd.append('file', f);
            try {
                document.getElementById('uploadStatus').innerText = '⏳ Загрузка...';
                const r = await fetch('/upload', {method: 'POST', body: fd});
                const d = await r.json();
                if (d.error) {
                    document.getElementById('uploadStatus').innerText = '❌ Ошибка: ' + d.error;
                } else {
                    document.getElementById('uploadStatus').innerText = 
                        '✓ Успешно! Обработано: ' + d.chunks + ' чанков, ' + 
                        Math.round(d.chars / 1024) + ' КБ';
                    loadStats();
                }
            } catch (e) {
                document.getElementById('uploadStatus').innerText = '❌ Ошибка: ' + e;
            }
        }

        async function ask() {
            const q = document.getElementById('q').value.trim();
            if (!q) {
                alert('Введите вопрос');
                return;
            }
            document.getElementById('res').classList.add('hidden');
            document.getElementById('loading').classList.remove('hidden');
            try {
                const r = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: q})
                });
                const d = await r.json();
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('res').classList.remove('hidden');
                document.getElementById('res').innerText = d.answer || ('❌ Ошибка: ' + d.error);
            } catch (e) {
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('res').classList.remove('hidden');
                document.getElementById('res').innerText = '❌ Ошибка сети: ' + e;
            }
        }

        async function clearDB() {
            if (confirm('Вы уверены? Это удалит все документы.')) {
                try {
                    const r = await fetch('/clear', {method: 'POST'});
                    const d = await r.json();
                    alert(d.message || 'База очищена');
                    loadStats();
                } catch (e) {
                    alert('Ошибка: ' + e);
                }
            }
        }

        loadStats();
    </script>
</body>
</html>
"""



# Вспомогательные функции
def extract_text_from_pdf(file_obj) -> str:
    """Извлечение текста из PDF файла"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Ошибка при чтении PDF: {e}")
        raise ValueError(f"Не удалось прочитать PDF: {str(e)}")


def extract_text_from_file(file_obj, filename: str) -> str:
    """Извлечение текста в зависимости от типа файла"""
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.pdf':
            return extract_text_from_pdf(file_obj)
        elif ext in ['.txt', '.md']:
            return file_obj.read().decode("utf-8", errors="ignore")
        elif ext == '.json':
            data = json.load(file_obj)
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
    except Exception as e:
        logger.error(f"Ошибка извлечения текста: {e}")
        raise


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Разбиение текста на чанки с перекрытием"""
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        if len(chunk.strip()) > 50:  # Игнорируем очень маленькие чанки
            chunks.append(chunk)
    return chunks


def get_system_prompt() -> str:
    """Системный промпт для LLM"""
    return """Вы - помощник по анализу документов. Отвечайте на основе предоставленного контекста.
    
Инструкции:
- Давайте точные и краткие ответы
- Если информация не в контексте, скажите "Этой информации нет в документе"
- Цитируйте релевантные части документа при необходимости
- Будьте вежливы и профессиональны"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/stats", methods=["GET"])
def stats():
    """Получить статистику по документам"""
    try:
        count = collection.count()
        docs = collection.get(include=["metadatas"])
        unique_docs = set()
        if docs.get("metadatas"):
            for meta in docs["metadatas"]:
                if meta.get("filename"):
                    unique_docs.add(meta["filename"])
        
        return jsonify({
            "chunks": count,
            "documents": len(unique_docs),
            "status": "ok"
        })
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload():
    """Загрузка и индексирование документа"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "Файл не загружен"}), 400
        
        f = request.files["file"]
        if f.filename == "":
            return jsonify({"error": "Выбран пустой файл"}), 400
        
        # Извлечение текста
        logger.info(f"Загрузка файла: {f.filename}")
        text = extract_text_from_file(f.stream, f.filename)
        
        if not text.strip():
            return jsonify({"error": "Файл пуст или не содержит текста"}), 400
        
        # Разбиение на чанки
        chunks = chunk_text(text)
        if not chunks:
            return jsonify({"error": "Не удалось обработать файл"}), 400
        
        # Создание эмбеддингов
        logger.info(f"Создание эмбеддингов для {len(chunks)} чанков...")
        embeddings = EMBED_MODEL.encode(chunks).tolist()
        
        # Добавление в базу с метаданными
        ids = [f"{f.filename}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "filename": f.filename,
                "chunk_index": i,
                "timestamp": datetime.now().isoformat()
            }
            for i in range(len(chunks))
        ]
        
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        logger.info(f"✓ Загружено {len(chunks)} чанков из {f.filename}")
        return jsonify({
            "status": "success",
            "chunks": len(chunks),
            "chars": len(text),
            "filename": f.filename
        })
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Ошибка загрузки: {e}")
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500


@app.route("/ask", methods=["POST"])
def ask():
    """Получить ответ на вопрос"""
    try:
        data = request.json
        if not data or "question" not in data:
            return jsonify({"error": "Вопрос не предоставлен"}), 400
        
        q = data["question"].strip()
        if not q:
            return jsonify({"error": "Вопрос не может быть пустым"}), 400
        
        if len(q) > 1000:
            return jsonify({"error": "Вопрос слишком длинный"}), 400
        
        # Проверка наличия документов
        if collection.count() == 0:
            return jsonify({
                "answer": "📚 База знаний пуста. Пожалуйста, загрузите документ."
            })
        
        # Поиск релевантного контекста
        logger.info(f"Поиск контекста для: {q[:50]}...")
        q_vec = EMBED_MODEL.encode(q).tolist()
        results = collection.query(
            query_embeddings=[q_vec],
            n_results=min(N_SEARCH_RESULTS, collection.count())
        )
        
        # Формирование контекста
        context_chunks = results["documents"][0] if results["documents"] else []
        context = "\n---\n".join(context_chunks)
        
        if not context.strip():
            return jsonify({
                "answer": "❌ Не найдена релевантная информация в документах."
            })
        
        logger.info(f"Найдено {len(context_chunks)} релевантных чанков")
        
        # Запрос к LLM
        try:
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: {q}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            answer = resp.choices[0].message.content
            logger.info("✓ Ответ получен успешно")
            return jsonify({"answer": answer})
        
        except Exception as llm_error:
            logger.error(f"Ошибка LLM: {llm_error}")
            return jsonify({
                "error": f"Ошибка при обращении к LLM: {str(llm_error)}"
            }), 503
    
    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {e}")
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500


@app.route("/clear", methods=["POST"])
def clear_db():
    """Очистить базу данных"""
    try:
        global collection
        chroma.delete_collection(name="rag_docs")
        collection = chroma.get_or_create_collection(
            name="rag_docs",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("✓ База данных очищена")
        return jsonify({"message": "✓ База данных успешно очищена"})
    except Exception as e:
        logger.error(f"Ошибка очистки БД: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "llm": LLM_BASE_URL,
        "chunks": collection.count()
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint не найден"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Внутренняя ошибка сервера: {e}")
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500


if __name__ == "__main__":
    logger.info(f"🚀 Запуск RAG приложения на http://0.0.0.0:{PORT}")
    logger.info(f"📊 Chroma DB: {CHROMA_DIR}")
    logger.info(f"🤖 LLM: {LLM_BASE_URL}")
    app.run(host="0.0.0.0", port=PORT, debug=False)

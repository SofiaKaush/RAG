import os
import chromadb
from flask import Flask, request, jsonify, render_template_string, Response
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import json

PORT = 5011
app = Flask(__name__)

# Инициализация базы данных и модели эмбеддингов
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
chroma = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma.get_or_create_collection(name="rag_docs")

# Клиент для LLM
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RAG Ассистент</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white p-8">
    <div class="max-w-3xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">Анализ корпоративных документов</h1>
        <div class="bg-slate-800 p-6 rounded-xl mb-6">
            <h2 class="text-xl mb-4">Загрузить документ (TXT)</h2>
            <input type="file" id="file" class="mb-4 text-sm text-slate-400">
            <button onclick="upload()" class="bg-blue-600 px-4 py-2 rounded">Загрузить</button>
        </div>
        <div class="bg-slate-800 p-6 rounded-xl">
            <input type="text" id="q" placeholder="Задайте вопрос..." class="w-full p-3 rounded text-slate-900 mb-2">
            <button onclick="ask()" class="bg-green-600 px-4 py-2 rounded">Спросить</button>
            <div id="res" class="mt-4 p-4 bg-slate-950 rounded whitespace-pre-wrap"></div>
        </div>
    </div>
    <script>
        async function upload() {
            const f = document.getElementById('file').files[0];
            const fd = new FormData(); fd.append('file', f);
            const r = await fetch('/upload', {method: 'POST', body: fd});
            const d = await r.json();
            alert('Статус: ' + d.status + '. Всего чанков: ' + d.chunks);
        }
        async function ask() {
            const q = document.getElementById('q').value;
            document.getElementById('res').innerText = 'Загрузка...';
            const r = await fetch('/ask', {
                method: 'POST', 
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: q})
            });
            const d = await r.json();
            document.getElementById('res').innerText = d.answer || 'Ошибка: ' + d.error;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    text = f.read().decode("utf-8", errors="ignore")
    chunks = [text[i:i+500] for i in range(0, len(text), 400)]
    embeddings = EMBED_MODEL.encode(chunks).tolist()
    ids = [f"id_{i}" for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings)
    print(f"DEBUG: Загружено {len(chunks)} чанков")
    return jsonify({"status": "success", "chunks": len(chunks)})

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("question")
    q_vec = EMBED_MODEL.encode(q).tolist()
    results = collection.query(query_embeddings=[q_vec], n_results=2)
    context = "\n".join(results["documents"][0])
    
    print(f"DEBUG: Вопрос: {q}")
    print(f"DEBUG: Найдено контекста: {len(context)} символов")
    
    if not context:
        return jsonify({"answer": "Не удалось найти информацию в базе. Попробуйте загрузить документ."})

    try:
        resp = client.chat.completions.create(
            model="local-model",
            messages=[{"role": "user", "content": f"Контекст: {context}\n\nВопрос: {q}"}]
        )
        return jsonify({"answer": resp.choices[0].message.content})
    except Exception as e:
        print(f"DEBUG: Ошибка LLM: {str(e)}")
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
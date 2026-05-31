#!/usr/bin/env python3
"""
Скрипт для тестирования RAG приложения
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5011"

def test_health():
    """Тест health endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print("✓ Health check:", resp.json())
        return True
    except Exception as e:
        print("✗ Health check failed:", e)
        return False

def test_stats():
    """Тест получения статистики"""
    try:
        resp = requests.get(f"{BASE_URL}/stats")
        print("✓ Stats:", resp.json())
        return True
    except Exception as e:
        print("✗ Stats failed:", e)
        return False

def test_upload():
    """Тест загрузки файла"""
    try:
        # Создаем тестовый файл
        with open("/tmp/test.txt", "w") as f:
            f.write("Это тестовый документ для RAG приложения. " * 50)
        
        with open("/tmp/test.txt", "rb") as f:
            files = {"file": f}
            resp = requests.post(f"{BASE_URL}/upload", files=files)
        print("✓ Upload response:", resp.json())
        return True
    except Exception as e:
        print("✗ Upload failed:", e)
        return False

def test_ask():
    """Тест задания вопроса"""
    try:
        data = {"question": "О чем этот документ?"}
        resp = requests.post(
            f"{BASE_URL}/ask",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        print("✓ Ask response:", resp.json())
        return True
    except Exception as e:
        print("✗ Ask failed:", e)
        return False

if __name__ == "__main__":
    print("🧪 Тестирование RAG приложения...\n")
    
    tests = [
        ("Health Check", test_health),
        ("Statistics", test_stats),
        ("Upload", test_upload),
        ("Ask", test_ask),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📝 {name}:")
        results.append(test_func())
    
    print(f"\n\n📊 Результаты: {sum(results)}/{len(results)} тестов пройдено")
    sys.exit(0 if all(results) else 1)

#!/bin/bash
# Manual Git commands - execute step by step

set -e

REPO="/workspaces/RAG"

echo "========================================="
echo "📦 Git Commit для RAG System"
echo "========================================="
echo ""

# Step 1
echo "📝 Шаг 1: Проверка статуса"
echo "Команда: git -C '$REPO' status"
echo "---"
exec git -C "$REPO" status


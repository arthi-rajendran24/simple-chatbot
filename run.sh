#!/usr/bin/env bash
# Start the profile chatbot at http://localhost:8181
cd "$(dirname "$0")"
MODEL="${CHAT_MODEL:-gemma4:e2b}"
command -v ollama >/dev/null || { echo "Install Ollama first: https://ollama.com/download"; exit 1; }
ollama list 2>/dev/null | grep -q "^${MODEL}" || ollama pull "$MODEL" || exit 1
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt; }
(sleep 2; open "http://localhost:${PORT:-8181}" 2>/dev/null || xdg-open "http://localhost:${PORT:-8181}" 2>/dev/null) &
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "${PORT:-8181}"

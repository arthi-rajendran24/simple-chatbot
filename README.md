# Profile Chat

A simple, private, agentic chatbot that answers questions **only** from profile documents (resumes, CVs, bios) you upload. It runs entirely on your machine using a local [Ollama](https://ollama.com) model. No data leaves your computer.

## How it works

1. **Upload** a PDF or DOCX in the web UI.
2. It's converted to **Markdown** and saved locally in `data/markdown/`.
3. When you ask a question, a tool-calling agent lists and reads those Markdown files and answers strictly from their content. If the answer isn't in them (or the question is unrelated), it says so instead of guessing.

There is no vector database or embeddings: the agent reads the files directly.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally
- A tool-calling-capable Ollama model (default: `gemma4:e2b`)

## Quick start

Prerequisites: [Python 3.10+](https://www.python.org/downloads/) (tick "Add python.exe to PATH" on Windows) and [Ollama](https://ollama.com/download) installed and running.

**Windows** (Command Prompt or PowerShell), one command:

```bat
git clone https://github.com/arthi-rajendran24/simple-chatbot.git && cd simple-chatbot && run.bat
```

**macOS / Linux**, one command:

```bash
git clone https://github.com/arthi-rajendran24/simple-chatbot.git && cd simple-chatbot && ./run.sh
```

The first run downloads the model (`gemma4:e2b`), creates a virtualenv and installs dependencies. After that it starts instantly and your browser opens **http://localhost:8181**.

## Using it

1. Drag & drop (or click to browse) your PDF/DOCX profile into the **Upload profile** box. You can upload several files.
2. Ask questions in the chat, e.g. *"Give me a summary"*, *"Where did she work?"*, *"What are the key skills?"*
3. Remove a document any time with the **×** next to it.

Tip: name each file after the person (e.g. `priya.docx`) when uploading several profiles. The agent uses filenames to pick the right document.

## Configuration

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `CHAT_MODEL` | `gemma4:e2b` | Ollama model used by the agent (must support tools) |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server address |
| `PORT` | `8181` | Web server port |

Example (macOS/Linux): `CHAT_MODEL=qwen3:8b PORT=9000 ./run.sh`. On Windows: `set CHAT_MODEL=qwen3:8b && set PORT=9000 && run.bat`.

## Project layout

```
app/agent.py   agent loop, tools, grounding rules
app/store.py   PDF/DOCX -> Markdown conversion and file storage
app/main.py    FastAPI endpoints (upload, documents, streaming chat)
static/        the chat UI (single HTML file)
```

## Limitations

- Scanned/image-only PDFs aren't supported (no OCR).
- Very long documents are truncated to ~6,000 characters when read.
- Small local models can occasionally make mistakes, especially across many profiles; a larger model improves accuracy.

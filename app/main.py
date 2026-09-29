import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, store
from .config import CHAT_MODEL, MAX_UPLOAD_MB, ROOT

app = FastAPI(title="Profile Chatbot")
STATIC = ROOT / "static"


class ChatRequest(BaseModel):
    messages: list[dict]  # [{role: user|assistant, content: str}]


@app.get("/api/info")
def info():
    return {"model": CHAT_MODEL}


@app.get("/api/documents")
def documents():
    return store.list_documents()


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    results = []
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in store.ALLOWED:
            results.append({"name": f.filename, "error": "Only PDF and DOCX are supported."})
            continue
        data = await f.read()
        if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
            results.append({"name": f.filename, "error": f"File exceeds {MAX_UPLOAD_MB} MB."})
            continue
        try:
            results.append(store.add_document(f.filename, data))
        except Exception as e:
            results.append({"name": f.filename, "error": str(e)})
    return results


@app.delete("/api/documents/{doc_id}")
def remove(doc_id: str):
    if not store.delete_document(doc_id):
        raise HTTPException(404, "Not found")
    return {"ok": True}


@app.post("/api/chat")
def chat(req: ChatRequest):
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in req.messages
        if m.get("role") in ("user", "assistant") and m.get("content")
    ][-20:]

    def stream():
        for event in agent.chat(history):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")

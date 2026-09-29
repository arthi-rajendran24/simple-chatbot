"""Uploaded profiles are converted to Markdown and stored as plain .md files."""
import io
import re
import uuid
from pathlib import Path

import pymupdf
import pymupdf4llm
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from .config import DATA_DIR

MD_DIR = DATA_DIR / "markdown"
MD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {".pdf", ".docx"}


def _docx_to_md(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    out: list[str] = []
    for block in doc.element.body.iterchildren():  # keep paragraphs/tables in order
        tag = block.tag.rsplit("}", 1)[-1]
        if tag == "p":
            p = Paragraph(block, doc)
            text = p.text.strip()
            if not text:
                continue
            style = (p.style.name or "").lower()
            if style == "title":
                out.append(f"# {text}")
            elif style.startswith("heading"):
                level = re.search(r"\d+", style)
                out.append("#" * min((int(level.group()) if level else 1) + 1, 6) + f" {text}")
            elif "list" in style:
                out.append(f"- {text}")
            else:
                out.append(text)
        elif tag == "tbl":
            rows = [
                [c.text.strip().replace("\n", " ") for c in r.cells]
                for r in Table(block, doc).rows
            ]
            rows = [r for r in rows if any(r)]
            if rows:
                out.append("| " + " | ".join(rows[0]) + " |")
                out.append("|" + " --- |" * len(rows[0]))
                out.extend("| " + " | ".join(r) + " |" for r in rows[1:])
        out.append("")
    return "\n".join(out)


def to_markdown(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        with pymupdf.open(stream=data, filetype="pdf") as pdf:
            return pymupdf4llm.to_markdown(pdf)
    if ext == ".docx":
        return _docx_to_md(data)
    raise ValueError("Only PDF and DOCX are supported.")


def add_document(filename: str, data: bytes) -> dict:
    md = re.sub(r"\n{3,}", "\n\n", to_markdown(filename, data)).strip()
    if len(md) < 20:
        raise ValueError("No readable text found. Scanned/image-only PDFs aren't supported.")
    doc_id = uuid.uuid4().hex[:10]
    stem = re.sub(r"[^\w\-. ]", "_", Path(filename).stem)
    (MD_DIR / f"{doc_id}__{stem}.md").write_text(md, encoding="utf-8")
    return {"id": doc_id, "name": f"{stem}.md", "chars": len(md)}


def _files() -> list[Path]:
    return sorted(MD_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime)


def list_documents() -> list[dict]:
    docs = []
    for p in _files():
        doc_id, name = p.name.split("__", 1)
        docs.append({"id": doc_id, "name": name, "chars": p.stat().st_size})
    return docs


def delete_document(doc_id: str) -> bool:
    found = False
    for p in MD_DIR.glob(f"{doc_id}__*.md"):
        p.unlink()
        found = True
    return found


def read_document(name: str) -> str | None:
    """Full markdown of the document whose filename contains `name` (case-insensitive)."""
    for d in list_documents():
        if name.lower().removesuffix(".md") in d["name"].lower():
            return (MD_DIR / f"{d['id']}__{d['name']}").read_text(encoding="utf-8")
    return None

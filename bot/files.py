"""Parse model-generated <file> blocks and turn them into downloadable documents."""
from __future__ import annotations

import io
import re
from dataclasses import dataclass

from .formatting import code_blocks

_FILE_TAG = re.compile(r'<file\s+name="([^"]+)"\s*>\n?(.*?)\n?</file>', re.S)
_SAFE = re.compile(r"[^A-Za-z0-9._\-]+")

EXT_BY_LANG = {
    "python": "py", "py": "py", "javascript": "js", "js": "js", "typescript": "ts", "ts": "ts",
    "html": "html", "css": "css", "json": "json", "yaml": "yaml", "yml": "yml", "bash": "sh",
    "sh": "sh", "sql": "sql", "java": "java", "go": "go", "rust": "rs", "c": "c", "cpp": "cpp",
    "csharp": "cs", "php": "php", "ruby": "rb", "swift": "swift", "kotlin": "kt", "markdown": "md",
    "md": "md", "xml": "xml", "csv": "csv", "text": "txt", "txt": "txt",
}

TEXT_EXTS = {
    ".txt", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".csv", ".html", ".css", ".xml",
    ".yaml", ".yml", ".sql", ".sh", ".java", ".go", ".rs", ".c", ".cpp", ".h", ".cs", ".php",
    ".rb", ".swift", ".kt", ".toml", ".ini", ".log", ".env", ".tex",
}


@dataclass
class GeneratedFile:
    name: str
    data: bytes


def safe_name(name: str) -> str:
    name = name.replace("\\", "/").split("/")[-1].strip()
    name = _SAFE.sub("_", name).strip("._") or "file.txt"
    return name[:80]


def parse_files(text: str) -> tuple[str, list[GeneratedFile]]:
    """Returns (message text without file blocks, files)."""
    files: list[GeneratedFile] = []
    for m in _FILE_TAG.finditer(text):
        name, body = safe_name(m.group(1)), m.group(2)
        if name.lower().endswith(".docx"):
            files.append(GeneratedFile(name, markdown_to_docx(body)))
        else:
            files.append(GeneratedFile(name, body.rstrip("\n").encode("utf-8") + b"\n"))
    rest = _FILE_TAG.sub("", text)
    rest = re.sub(r"<file\s+name=.*\Z", "", rest, flags=re.S)  # unterminated block (cut off)
    return rest.strip(), files


def answer_to_file(text: str) -> GeneratedFile:
    """Pick the best file representation of a chat answer."""
    blocks = code_blocks(text)
    if len(blocks) == 1 and len(blocks[0][1]) > len(text) * 0.35:
        lang, code = blocks[0]
        ext = EXT_BY_LANG.get(lang, "txt")
        return GeneratedFile(f"answer.{ext}", code.rstrip("\n").encode() + b"\n")
    return GeneratedFile("answer.md", text.strip().encode() + b"\n")


def _add_runs(paragraph, text: str) -> None:
    for part in re.split(r"(\*\*[^*]+\*\*)", text):
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            paragraph.add_run(part[2:-2]).bold = True
        elif part:
            paragraph.add_run(part.replace("`", ""))


def markdown_to_docx(md: str) -> bytes:
    from docx import Document

    doc = Document()
    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if m := re.match(r"^(#{1,4})\s+(.*)", line):
            doc.add_heading(m.group(2).strip("# ").replace("**", ""), level=min(len(m.group(1)), 4))
        elif m := re.match(r"^\s*[-*+]\s+(.*)", line):
            _add_runs(doc.add_paragraph(style="List Bullet"), m.group(1))
        elif m := re.match(r"^\s*\d+[.)]\s+(.*)", line):
            _add_runs(doc.add_paragraph(style="List Number"), m.group(1))
        elif re.match(r"^-{3,}$", line):
            doc.add_paragraph("")
        else:
            _add_runs(doc.add_paragraph(), line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

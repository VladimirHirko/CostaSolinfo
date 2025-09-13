#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
from datetime import datetime

# Корень проекта — текущая директория
ROOT = os.path.abspath(os.getcwd())
OUT_FILE = f"CODE_SNAPSHOT_2025-09-13.md"

# Исключённые директории (не обходить)
EXCLUDE_DIRS = {
    ".git", "node_modules", "venv", "env", "__pycache__", ".idea", ".vscode",
    "build", "dist", ".cache", "coverage", "media", "staticfiles"
}

# Исключённые по именам файлов/маскам (простые окончания)
EXCLUDE_SUFFIXES = {
    ".sqlite3", ".log", ".lock", ".pyc", ".pyo", ".so", ".dylib",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".tiff", ".bmp", ".ico",
    ".psd", ".zip", ".rar", ".7z", ".pdf", ".DS_Store"
}

# Какие расширения включать (текстовые исходники)
INCLUDE_EXTS = {
    # backend / python / infra
    ".py", ".ini", ".cfg", ".toml", ".yaml", ".yml", ".sh", ".env", ".env.example",
    # frontend
    ".js", ".jsx", ".ts", ".tsx", ".json", ".html", ".css",
    # docs
    ".md", ".txt"
}

# Карта расширений к языку для Markdown-фенсов
LANG_BY_EXT = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".sh": "bash",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".md": "",    # пусть без подсветки
    ".txt": "",
    ".env": "",   # без подсветки
}

def is_excluded_dir(path_parts):
    return any(part in EXCLUDE_DIRS for part in path_parts)

def should_skip_file(fname):
    lower = fname.lower()
    return any(lower.endswith(suf) for suf in EXCLUDE_SUFFIXES)

def is_included_file(fname):
    lower = fname.lower()
    return any(lower.endswith(ext) for ext in INCLUDE_EXTS)

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def detect_lang(fname):
    lower = fname.lower()
    for ext, lang in LANG_BY_EXT.items():
        if lower.endswith(ext):
            return lang
    return ""  # по умолчанию без подсветки

def relpath(path):
    return os.path.relpath(path, ROOT)

def main():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Фильтруем директории на месте — чтобы os.walk в них не заходил
        parts = os.path.relpath(dirpath, ROOT).split(os.sep)
        if parts == ['.']:
            parts = []
        if is_excluded_dir(parts):
            dirnames[:] = []  # не заходить глубже
            continue

        # Сортируем, чтобы снимок был стабильным
        dirnames.sort()
        filenames.sort()

        for fname in filenames:
            if should_skip_file(fname):
                continue
            if not is_included_file(fname):
                continue

            path = os.path.join(dirpath, fname)
            files.append(path)

    files.sort(key=lambda p: relpath(p))

    with open(OUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"# Code Snapshot — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        out.write(f"**Project root:** `{ROOT}`\n\n")
        out.write("> Сгенерировано автоматически. Исключены служебные/бинарные директории и файлы.\n\n")
        out.write("---\n\n")

        for path in files:
            rp = relpath(path)
            try:
                size = os.path.getsize(path)
                sha = file_sha256(path)
                lang = detect_lang(path)
                out.write(f"## `{rp}`  \n")
                out.write(f"- size: `{size}` bytes  \n- sha256: `{sha}`\n\n")
                out.write("```" + (lang or "") + "\n")
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    out.write(f.read())
                out.write("\n```\n\n---\n\n")
            except Exception as e:
                out.write(f"## `{rp}`\n")
                out.write(f"> Не удалось прочитать файл: {e}\n\n---\n\n")

    print(f"✓ Готово: {OUT_FILE}")

if __name__ == "__main__":
    main()

cat > tools/make_tree.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

DATE="$(date +%F)"
DOCS_DIR="docs"
mkdir -p "$DOCS_DIR"

IGNORE_DIRS='venv|.venv|__pycache__|node_modules|.next|.nuxt|dist|build|coverage|.cache|.pytest_cache|.mypy_cache|.git|media|staticfiles|.DS_Store'

if command -v tree >/dev/null 2>&1; then
  tree -a -I "$IGNORE_DIRS" > "$DOCS_DIR/CostaSolinfo_tree_${DATE}.txt"
  echo "✅ Сохранено: $DOCS_DIR/CostaSolinfo_tree_${DATE}.txt"
else
  echo "ℹ️ 'tree' не найден — запускаю Python-fallback"
  python3 tools/make_tree.py
fi
SH

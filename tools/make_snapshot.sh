set -euo pipefail
DATE=$(date +%F)
TREE_OUT="Docs/PROJECT_TREE_${DATE}.txt"
SNAP_OUT="Docs/CODE_SNAPSHOT_${DATE}.md"
IGNORE_DIRS="node_modules|venv|.git|__pycache__|build|dist|.next|coverage|media|staticfiles|*.pyc|*.pyo|*.sqlite3"
FILES=(
  # --- backend (django) ---
  "backend/manage.py"
  "backend/backend/settings.py"
  "backend/backend/urls.py"
  "backend/core/apps.py"
  "backend/core/models.py"
  "backend/core/admin.py"
  "backend/core/forms.py"
  "backend/core/utils.py"
  "backend/core/signals.py"
  "backend/core/views.py"
  "backend/core/urls.py"
  "backend/core/serializers.py"
  "backend/core/management/commands/audit_excursion_zones.py"
  "backend/templates/admin/core/excursions_import.html"
  "backend/templates/admin/core/excursionpickuppoint/change_list.html"
  "backend/templates/admin/core/transferschedulegroup/change_list.html"
  "backend/templates/admin/core/transferschedulegroup/import.html"
  "backend/static/admin/js/excursion_pickup_autofill.js"
  "backend/static/admin/js/pickup_point_map.js"

  # --- frontend (react/vite) ---
  "frontend/src/index.js"
  "frontend/src/App.js"
  "frontend/src/i18n.js"
  "frontend/src/pages/HomePage.js"
  "frontend/src/pages/ExcursionsPage.js"
  "frontend/src/pages/ExcursionDetailPage.js"
  "frontend/src/pages/AirportTransferPage.js"
  "frontend/src/pages/AirportTransferGroupPage.js"
  "frontend/src/pages/AirportTransferPrivatePage.js"
  "frontend/src/pages/AskQuestionPage.js"
  "frontend/src/pages/ContactsPage.js"
  "frontend/src/pages/InfoMeetingPage.js"
  "frontend/src/components/Navbar.js"
  "frontend/src/components/Footer.js"
  "frontend/src/components/PageBanner.js"
  "frontend/src/components/TransferMap.js"
  "frontend/src/components/PickupMap.js"
  "frontend/src/components/PrivacyPolicyModal.js"
  "frontend/src/components/Breadcrumbs.jsx"
  "frontend/src/helpers/normalizeText.js"
  "frontend/src/hooks/usePageContent.js"
  "frontend/src/styles/main.css"
  "frontend/src/styles/ExcursionsPage.css"
  "frontend/src/styles/ExcursionDetailPage.css"
  "frontend/src/styles/Footer.css"
  "frontend/src/styles/breadcrumbs.css"
  "frontend/src/pages/HomePage.css"
  # локали — чтобы не раздувать файлик, включим хотя бы ru/en:
  "frontend/src/locales/ru/translation.json"
  "frontend/src/locales/en/translation.json"
)
# --- 1) дерево проекта ---
if command -v tree >/dev/null 2>&1; then
  tree -a -I "${IGNORE_DIRS}" > "${TREE_OUT}"
else
  # простой fallback без tree
  find . -type d \
    | grep -Ev "/(${IGNORE_DIRS})($|/)" \
    | sed 's/[^-][^\/]*\//  /g;s/\/$//' > "${TREE_OUT}"
fi
echo "✓ Project tree saved to: ${TREE_OUT}"

# --- 2) Markdown-снапшот кода ---
: > "${SNAP_OUT}"  # очистить/создать файл
echo "# Code Snapshot — ${DATE}" >> "${SNAP_OUT}"

append_file () {
  local f="$1"
  [ -f "$f" ] || return 0
  # определяем язык подсветки по расширению
  local ext="${f##*.}"; local lang="$ext"
  case "$ext" in
    js|jsx) lang="js" ;;
    py)     lang="py" ;;
    css)    lang="css" ;;
    html|htm) lang="html" ;;
    json)   lang="json" ;;
    md)     lang="" ;;
    *)      lang="" ;;
  esac
  echo -e "\n---\n## ${f}\n" >> "${SNAP_OUT}"
  if [ -n "${lang}" ]; then
    echo "\`\`\`${lang}" >> "${SNAP_OUT}"
  else
    echo "\`\`\`" >> "${SNAP_OUT}"
  fi
  cat "$f" >> "${SNAP_OUT}"
  echo -e "\n\`\`\`" >> "${SNAP_OUT}"
}

for pattern in "${FILES[@]}"; do
  # паттерн может быть с пробелами/юникодом — обрабатываем аккуратно
  # разрешим и подстановку масок, если пользователь их добавит
  for f in $pattern; do
    append_file "$f"
  done
done

echo "✓ Code snapshot saved to: ${SNAP_OUT}"

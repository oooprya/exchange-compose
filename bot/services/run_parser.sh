#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$PROJECT_DIR/venv" ]; then

echo "$PROJECT_DIR/venv"
  # python3 -m venv venv
  # venv/bin/pip install -r requirements.txt
  # venv/bin/playwright install chromium
  # venv/bin/playwright install-deps 
fi

cd "$PROJECT_DIR"

# запуск python из venv проекта
"$PROJECT_DIR/venv/bin/python" parser_bank.py
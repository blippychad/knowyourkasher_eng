#!/usr/bin/env bash
set -e
mkdir -p fonts presets
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-build.txt
pyinstaller --noconfirm --windowed --onedir --name QuizShow --add-data "fonts:fonts" --add-data "presets:presets" quizshow_app_en.py
echo "Build finished. Output folder: dist/QuizShow"
echo "On macOS, if Gatekeeper warns you, open the app with right-click > Open or remove quarantine manually."

#!/usr/bin/env bash
set -e
mkdir -p fonts presets
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python quizshow_app_en.py

@echo off
if not exist fonts mkdir fonts
if not exist presets mkdir presets
if not exist .venv py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python quizshow_app_en.py
pause

@echo off
if not exist fonts mkdir fonts
if not exist presets mkdir presets
if not exist .venv py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-build.txt
pyinstaller --noconfirm --windowed --onedir --name QuizShow --add-data "fonts;fonts" --add-data "presets;presets" quizshow_app_en.py
echo.
echo Build finished. Output folder: dist\QuizShow
pause

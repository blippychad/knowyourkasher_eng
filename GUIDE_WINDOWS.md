# QuizShow on Windows

## Run without compiling

1. Open the project folder in Command Prompt or PowerShell.
2. Run `run_windows.bat`.
3. The script creates a virtual environment, installs dependencies, and starts the app from source.

### Manual commands

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python quizshow_app_en.py
```

## Compile to an executable

1. Run `build_windows.bat`.
2. Wait until PyInstaller finishes.
3. Open `dist\QuizShow`.
4. Launch the built application from that folder.

### Manual commands

```bat
.venv\Scripts\activate
pip install -r requirements-build.txt
pyinstaller --noconfirm --windowed --onedir --name QuizShow --add-data "fonts;fonts" --add-data "presets;presets" quizshow_app_en.py
```

## Notes

- Keep `fonts/` and `presets/` in the project folder.
- Test at least one video answer after the build.
- If SmartScreen complains, use More info > Run anyway only if you trust your own build.

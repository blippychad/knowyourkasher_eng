# QuizShow on Linux

## Run without compiling

1. Open a terminal in the project folder.
2. Run `./run_linux.sh`.
3. The script creates a virtual environment, installs dependencies, and starts the app from source.

### Manual commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python quizshow_app_en.py
```

## Compile to an executable

1. Run `./build_linux.sh`.
2. Wait until PyInstaller finishes.
3. Open `dist/QuizShow`.
4. Start the built application from that folder.

### Manual commands

```bash
source .venv/bin/activate
pip install -r requirements-build.txt
pyinstaller --noconfirm --windowed --onedir --name QuizShow --add-data "fonts:fonts" --add-data "presets:presets" quizshow_app_en.py
```

## Notes

- Some Linux distributions may require extra multimedia codecs for video playback.
- Keep `fonts/` and `presets/` in the project folder.
- If the shell scripts are not executable, run `chmod +x build_linux.sh run_linux.sh`.

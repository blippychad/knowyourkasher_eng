# QuizShow on macOS

## Run without compiling

1. Open Terminal in the project folder.
2. Run `./run_mac.sh`.
3. The script creates a virtual environment, installs dependencies, and starts the app from source.

### Manual commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python quizshow_app_en.py
```

## Compile to an application build

1. Run `./build_mac.sh`.
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

- Keep `fonts/` and `presets/` in the project folder.
- macOS Gatekeeper may block an unsigned build; right-click > Open can help for local testing.
- Test at least one video answer on the target Mac before sharing the app.

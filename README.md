# Shipyard

Shipyard is a Windows system tray application with a local PWA dashboard for launching and monitoring self-hosted services.

## Run from source

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Start the app:
   - `python main.py`

## Build executable

- `pyinstaller shipyard.spec --clean`

The built executable is output to `dist/shipyard.exe`.

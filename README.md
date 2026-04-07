# Shipyard

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Platform](https://img.shields.io/badge/Platform-Windows%2011-blue) ![License](https://img.shields.io/badge/License-MIT-purple) ![Release](https://img.shields.io/github/v/release/Vistiqx/Shipyard)

📖 5 minute read

Shipyard is a Windows 11 system tray application that gives you one-click access to the web interfaces of Docker containers running on your home lab or private servers. It runs silently in the background, monitors the health of your services, and opens any container's web UI in your browser with a single click. A built-in PWA dashboard is also available at `http://127.0.0.1:9999` for a full visual overview of all your services.

> **Screenshots coming soon**

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Quick Start — End Users](#quick-start--end-users)
- [Configuration](#configuration)
- [Using the System Tray](#using-the-system-tray)
- [Using the PWA Dashboard](#using-the-pwa-dashboard)
- [Health Monitoring](#health-monitoring)
- [Building from Source](#building-from-source)
- [Project Structure](#project-structure)
- [Configuration File Location](#configuration-file-location)
- [REST API](#rest-api)
- [Troubleshooting](#troubleshooting)
- [Adding Application Logos](#adding-application-logos)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features

- **System tray icon with popup menu** — one click to open any container's web UI
- **Live health monitoring** — green, amber, and red status for every service
- **PWA dashboard at localhost:9999** — full tile grid view with search and filtering
- **Application logos** — automatically loaded from the homarr-labs dashboard-icons CDN
- **Status left-border on tiles** — instant visual health indicator on every card
- **Multiple server support** — organize containers into server groups
- **Port-aware URLs** — each application uses its correct host port
- **Path suffix support** — for apps like Pi-hole that require `/admin`
- **TCP/UDP service visibility** — non-HTTP services shown as informational entries
- **Full application management** — add, edit, enable, disable, and remove via GUI
- **First-run setup wizard** — config file created automatically with Notepad on first launch
- **Launch at Windows startup** — optional, configurable in Settings
- **Single standalone exe** — no Python installation required for end users
- **Auto health checks** — polls every 60 seconds with manual refresh available
- **Installable PWA** — install from Edge or Chrome as a native-feeling desktop app
- **Completely local** — the API server binds to 127.0.0.1 only, never exposed to your LAN

---

## How It Works

Shipyard runs as a lightweight background process in the Windows system tray. It reads a simple YAML configuration file (`servers.yaml`) that tells it which containers exist, where they live on your network, and which ports their web interfaces are exposed on. From this file it builds the tray menu and the PWA dashboard automatically.

Every 60 seconds — and on demand when you click Refresh — Shipyard sends an HTTP GET request to each enabled application. It classifies the response as green (reachable), amber (responding with an error), or red (unreachable or timed out). These results update both the tray icon glyphs and the PWA tile borders in real time. Self-signed HTTPS certificates are accepted without error so internal services with private certs work out of the box.

The PWA dashboard is served by a minimal HTTP server that Shipyard starts automatically on `127.0.0.1:9999`. This server also exposes a REST API that the dashboard uses to read status, trigger health checks, and manage the configuration. Because it binds to localhost only, it is never accessible from other machines on your network.

When you click a service — either in the tray or in the PWA — Shipyard constructs the full URL from the protocol, IP address, port, and optional path suffix defined in your config, then opens it in your default browser. The browser handles authentication and everything else from that point forward.

---

## Requirements

### To run the exe (end users)

- Windows 10 or Windows 11 (64-bit)
- No Python installation required
- LAN access to your Docker hosts
- Edge or Chrome recommended for PWA installation

### To build from source (developers)

- Windows 10 or Windows 11 (64-bit)
- Python 3.11 or higher
- pip
- Git

---

## Quick Start — End Users

1. Go to the [Releases](https://github.com/Vistiqx/Shipyard/releases) page and download `shipyard.exe`
2. Create a folder anywhere on your machine, e.g. `C:\Shipyard\`
3. Place `shipyard.exe` in that folder
4. Double-click `shipyard.exe`
5. On first run, Shipyard creates a config file at `config\servers.yaml` in the same folder as the exe
6. Notepad opens automatically with the config file
7. Edit the file to add your servers and applications — see [Configuration](#configuration)
8. Save the file and restart Shipyard
9. The Shipyard icon appears in your system tray — click it to see your containers
10. **Optional:** install the PWA by navigating to `http://127.0.0.1:9999` in Edge or Chrome and clicking `...` → Apps → Install this site as an app

> **Tip:** If you don't see the Shipyard icon in the taskbar, it may be in the notification area overflow. Right-click the taskbar → Taskbar settings → Other system tray icons → enable Shipyard.

---

## Configuration

### The config file

Shipyard reads all of its configuration from a single YAML file: `config\servers.yaml`, located in the same folder as `shipyard.exe`. This file is created automatically from the included template on first run. It is plain text and safe to edit in any text editor — Notepad, VS Code, Notepad++, or anything else.

Restart Shipyard after saving changes for them to take effect, or use the Settings dialog inside the app to make changes without editing the file directly.

> ⚠️ **Never commit `servers.yaml` to a public repository.** It contains your private network topology including IP addresses and port mappings. See [Building from Source](#building-from-source) for how this is handled in the development workflow.

### Full schema

```yaml
settings:
  pwa_first_run: true                   # true = open browser automatically on first launch
  launch_at_startup: true               # true = start Shipyard when Windows starts
  health_check_interval_seconds: 60     # how often to ping all services (10–3600)
  health_check_timeout_seconds: 5       # per-request timeout in seconds (1–30)
  default_protocol: http                # fallback protocol if not specified per app

servers:
  - name: MY-SERVER                     # display name shown as a group header
    applications:
      - name: My Application            # display name shown in tray and PWA tile
        ip: 192.168.1.100               # IP address or hostname of the container host
        port: 8080                      # host port the web UI is exposed on
        protocol: http                  # http | https | tcp | udp
        path: ""                        # optional URL path suffix e.g. /admin
        enabled: true                   # true = shown and monitored, false = hidden
```

### Field reference

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` (server) | string | yes | — | Display name for the server group in the tray and PWA |
| `name` (app) | string | yes | — | Display name shown on the tray item and PWA tile |
| `ip` | string | yes | — | IP address or hostname of the Docker host |
| `port` | integer | yes | — | Host port the container's web UI is mapped to |
| `protocol` | string | yes | `http` | `http`, `https`, `tcp`, or `udp` |
| `path` | string | no | `""` | URL path suffix appended to the base URL e.g. `/admin` |
| `enabled` | boolean | no | `true` | Whether the application is shown and health checked |
| `launch_at_startup` | boolean | no | `true` | Register Shipyard in the Windows startup registry |
| `health_check_interval_seconds` | integer | no | `60` | Seconds between automatic health check passes |
| `health_check_timeout_seconds` | integer | no | `5` | Seconds before a health check request times out |

### Protocol types

| Protocol | Web UI | Health Checked | Clickable |
|---|---|---|---|
| `http` | Yes | Yes | Yes |
| `https` | Yes | Yes | Yes |
| `tcp` | No | No | No |
| `udp` | No | No | No |

TCP and UDP services — such as databases, DNS servers, and RADIUS — are included in the config for inventory visibility. They appear in the PWA as greyed-out tiles and are excluded from the tray menu. They are never health checked and cannot be opened in a browser.

### Path suffix

Some applications serve their UI at a subpath rather than the root URL. For example, Pi-hole's admin panel lives at `http://192.168.1.229:8053/admin` rather than `http://192.168.1.229:8053`. Set `path: /admin` for these applications and Shipyard will append it automatically when building the URL.

### Adding a new application

There are three ways to add an application:

1. **Edit `servers.yaml` directly** — add an entry under the appropriate server and restart Shipyard
2. **Tray menu** — click the `＋` icon at the top of the tray popup and fill in the dialog
3. **PWA dashboard** — click the `＋` icon in the top bar and fill in the modal

### Enabling and disabling

Set `enabled: false` to hide an application from the tray menu and show it as a greyed-out tile in the PWA. This is useful for services that are temporarily offline, under maintenance, or that have no web UI such as databases and DNS servers.

---

## Using the System Tray

The Shipyard icon lives in the Windows notification area (system tray) at the right end of the taskbar. Left-click or right-click the icon to open the popup menu.

The menu is organized by server group. Each application entry shows a status glyph on the left and the full IP:port address on the right. Click any application to open its web UI in your default browser.

**Status glyphs:**

| Glyph | Meaning |
|---|---|
| `●` | Online — reachable and responding normally |
| `◑` | Degraded — responding but returning an error status |
| `○` | Offline — unreachable or timed out |
| `·` | Unknown — not yet checked since last startup |

**Header icons at the top of the menu:**

| Icon | Action |
|---|---|
| `↺` | Refresh — immediately re-runs all health checks |
| `＋` | Add application — opens the add application dialog |
| `⚙` | Settings — opens the settings and management panel |
| `?` | Help — opens the documentation window |

TCP and UDP services do not appear in the tray menu — they are only visible in the PWA dashboard.

When one or more services are offline the tray icon displays a red alert indicator so you can see at a glance that something needs attention without opening the menu.

---

## Using the PWA Dashboard

Navigate to `http://127.0.0.1:9999` in Edge or Chrome while Shipyard is running to open the dashboard. Shipyard will also open it automatically in your browser the first time it launches.

The dashboard shows all applications as tiles organized by server group. Each tile displays:

- The application logo (loaded from the homarr-labs CDN)
- Application name
- Full IP address and port badge
- Status dot in the top-right corner
- Colored left border — green, amber, red, or gray matching the health status

Click any tile to open the application in a new browser tab. TCP/UDP tiles are greyed out and not clickable. The search bar at the top filters tiles by application name or IP address as you type. The status bar at the bottom shows total counts and the time of the last health check. The dashboard auto-refreshes every 30 seconds and you can trigger an immediate refresh with the `↺` button.

All management actions are available in the PWA: add, edit, remove, enable/disable applications, manage server groups, and update global settings. Clicking `⚙` in the tray menu opens the PWA settings panel directly.

### Installing as a PWA

Installing Shipyard as a PWA gives it its own taskbar button, Start Menu entry, and standalone window with no browser chrome — indistinguishable from a native app.

**In Microsoft Edge:**
1. Navigate to `http://127.0.0.1:9999`
2. Click `...` → Apps → Install this site as an app
3. Click Install
4. Shipyard appears in your taskbar and Start Menu

**In Google Chrome:**
1. Navigate to `http://127.0.0.1:9999`
2. Click the install icon in the address bar (looks like a monitor with a down arrow)
3. Click Install

> **Note:** Shipyard must be running for the PWA to be available. The PWA itself does not require internet access — only the application logos are loaded from an external CDN. If you are offline, two-letter initials are shown instead.

---

## Health Monitoring

Shipyard sends an HTTP GET request to the root URL of each enabled `http` or `https` application. Checks run automatically on startup and then on the configured interval (default 60 seconds). Results are cached and reflected immediately in the tray menu glyphs and the PWA tile colors and borders.

| Status | Color | Trigger |
|---|---|---|
| Online | Green `#1D9E75` | HTTP response 200–399 |
| Degraded | Amber `#BA7517` | HTTP response 400–599 or connection refused |
| Offline | Red `#E24B4A` | Request timed out or no route to host |
| Unknown | Gray `#6E6E80` | Not yet checked since last startup |

Health checks run in parallel threads — one thread per server group — so a slow or unreachable server does not delay checks for other servers. Self-signed HTTPS certificates are accepted without error. TCP and UDP protocol entries are never health checked.

---

## Building from Source

### Clone the repository

```bash
git clone https://github.com/Vistiqx/Shipyard.git
cd Shipyard
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set up your config

```bash
copy config\servers.yaml.template config\servers.yaml
```

Open `config\servers.yaml` in a text editor and replace the placeholder `10.0.0.x` addresses with your real server IPs, ports, and application names.

### Run in development mode

Set the `SHIPYARD_CONFIG` environment variable so Shipyard loads your real config instead of looking for a default:

```batch
set SHIPYARD_CONFIG=C:\path\to\Shipyard\config\servers.yaml
python main.py
```

For convenience, create a `run_local.bat` file in the project root:

```batch
@echo off
set SHIPYARD_CONFIG=%~dp0config\servers.yaml
python "%~dp0main.py"
```

Double-click `run_local.bat` to start Shipyard in development mode at any time. Add `run_local.bat` to your `.gitignore` if it contains any local paths.

### Build the standalone exe

```bash
pyinstaller shipyard.spec --clean
```

Output: `dist\shipyard.exe`

The exe is fully self-contained and includes the Python 3.11 runtime, all pip dependencies, all PWA files, the tray icon assets, and `servers.yaml.template` as the default config for new users. It does not include your real `servers.yaml`.

### Verify the build is clean

After building, confirm no real IP addresses were accidentally bundled:

```python
python -c "
with open(r'dist\shipyard.exe', 'rb') as f:
    content = f.read().decode('latin-1')
for p in ['192.168.1.', '192.168.239.']:
    if p in content:
        print(f'FAIL: Found {p} in exe')
    else:
        print(f'PASS: {p} not found')
"
```

### Important: never commit servers.yaml

Your real `servers.yaml` contains private network topology — IP addresses, ports, and service names. It is listed in `.gitignore` and will never be staged or pushed by git. Only `servers.yaml.template` (which contains placeholder `10.0.0.x` addresses) is tracked in the repository. This is intentional and mirrors the `.env` / `.env.example` pattern used by most open source projects.

---

## Project Structure

```
Shipyard\
├── assets\                   # Tray icon source files (auto-generated by Pillow on build)
│   ├── icon.png              # 64x64 tray icon
│   ├── icon_alert.png        # 64x64 tray icon with red alert dot
│   └── icon.ico              # Multi-size ICO for PyInstaller
├── config\
│   ├── servers.yaml          # YOUR config — gitignored, never commit this
│   └── servers.yaml.template # Safe placeholder template — tracked in git
├── dist\                     # PyInstaller build output — gitignored
│   └── shipyard.exe          # Standalone distributable executable
├── docs\
│   └── help_content.py       # Inline help documentation and FAQ content
├── pwa\                      # PWA frontend — all served by the local HTTP server
│   ├── index.html            # Single-page app shell and all CSS styles
│   ├── app.js                # All frontend JavaScript (vanilla JS, no frameworks)
│   ├── manifest.json         # PWA manifest for browser installability
│   ├── sw.js                 # Service worker for offline shell caching
│   ├── icon-192.png          # PWA icon 192x192 (auto-generated by Pillow)
│   └── icon-512.png          # PWA icon 512x512 (auto-generated by Pillow)
├── ui\
│   ├── add_app_dialog.py     # tkinter dialog: add and edit applications
│   ├── settings_dialog.py    # tkinter dialog: manage servers, apps, startup registry
│   └── help_window.py        # tkinter window: scrollable documentation and FAQ
├── .gitignore                # Excludes servers.yaml, dist/, build/, generated assets
├── BUILD_NOTES.md            # PyInstaller build warnings and notes
├── README.md                 # This file
├── TEST_RESULTS.md           # End-to-end test results from last test run
├── config.py                 # Config loader, validator, path resolution, CRUD functions
├── health.py                 # Threaded HTTP health check engine
├── main.py                   # Entry point: tray icon, menu, startup logic, first-run wizard
├── server.py                 # Local HTTP server and REST API for the PWA
├── shipyard.spec             # PyInstaller build specification
└── requirements.txt          # Python dependencies with pinned versions
```

---

## Configuration File Location

Shipyard resolves the config file path in the following order of precedence:

| Scenario | Config loaded from |
|---|---|
| `SHIPYARD_CONFIG` env var is set | The path specified by `SHIPYARD_CONFIG` |
| Running `shipyard.exe`, file exists | `config\servers.yaml` next to the exe |
| Running `shipyard.exe`, first run | Template copied to `config\servers.yaml` automatically |
| Running `python main.py`, no env var | `config\servers.yaml` next to `main.py` |

The `SHIPYARD_CONFIG` environment variable is intended for development use so you can point to your real config while running from source without it being picked up by the distributed exe.

---

## REST API

The PWA communicates with Shipyard via a local REST API. All endpoints are available at `http://127.0.0.1:9999/api`. The server binds to `127.0.0.1` only and is never accessible from other machines on your network.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Health status and metadata for all applications |
| `GET` | `/api/config` | Full current configuration as JSON |
| `POST` | `/api/refresh` | Trigger an immediate health check pass |
| `POST` | `/api/application/add` | Add a new application to a server group |
| `POST` | `/api/application/edit` | Edit an existing application |
| `POST` | `/api/application/remove` | Remove an application |
| `POST` | `/api/application/toggle` | Enable or disable an application |
| `POST` | `/api/server/add` | Add a new server group |
| `POST` | `/api/server/remove` | Remove a server group and all its applications |
| `POST` | `/api/settings/update` | Update global settings (interval, timeout, startup) |

The `/api/status` response includes a `summary` object with counts of online, degraded, offline, and unknown services, plus a `last_check` ISO 8601 timestamp of the last completed health check pass.

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---|---|---|
| Tray icon not visible | Hidden in notification overflow | Right-click taskbar → Taskbar settings → Other system tray icons → enable Shipyard |
| All services show red | Wrong IP or port in config | Verify the IP and port in `servers.yaml` match the container's **host** port mapping, not the internal container port |
| Service shows red but is running | Path suffix missing or wrong port | Check the container's `docker-compose.yml` — the host port is the left side of the port mapping e.g. `8021:8000` means host port `8021` |
| HTTPS service shows red | Wrong IP or port | Shipyard accepts self-signed certs automatically — the issue is the address, not the certificate |
| PWA won't load at localhost:9999 | Shipyard is not running | Start Shipyard first — the PWA requires the local server |
| Port 9999 conflict | Another process using port 9999 | Stop the conflicting process or change which service uses that port |
| Application logos not showing | No internet access | Logos load from the homarr-labs CDN — two-letter initials are shown as a fallback when offline |
| Welcome dialog appears every launch | `servers.yaml` being deleted or moved | Ensure `servers.yaml` exists at `config\servers.yaml` in the same folder as the exe and is not being cleaned up |
| Wrong config being loaded | `SHIPYARD_CONFIG` env var is set | Run `set SHIPYARD_CONFIG=` to clear it, or point it to the correct file |
| Multiple instances warning | Lock file left behind after a crash | Delete `%TEMP%\shipyard.lock` and relaunch |
| Settings changes not saving | File permission issue | Ensure Shipyard has write access to the `config\` folder next to the exe |
| Startup on Windows not working | Exe path changed after registering | Re-enable startup in Settings to rewrite the registry key with the current exe path |

---

## Adding Application Logos

Application logos are loaded from the [homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons) CDN at:

```
https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/{icon-name}.svg
```

The mapping between application names and icon filenames is defined in `ICON_MAP` at the top of `pwa/app.js`. If an application name is not found in `ICON_MAP`, Shipyard automatically shows two-letter initials as a fallback.

To add a logo for a custom application:

1. Search for the icon at [dashboardicons.com](https://dashboardicons.com)
2. Note the filename — icons use kebab-case lowercase, e.g. `my-app.svg`
3. Open `pwa/app.js` and add an entry to `ICON_MAP`:

```javascript
const ICON_MAP = {
  // existing entries...
  'My Application': 'my-app.svg',
};
```

If no icon exists for your application on dashboardicons.com, the two-letter initials fallback will be used automatically — no action needed.

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```
2. Make your changes and test locally:
   ```bash
   set SHIPYARD_CONFIG=C:\path\to\config\servers.yaml
   python main.py
   ```
3. Build and verify the exe is clean:
   ```bash
   pyinstaller shipyard.spec --clean
   ```
4. Submit a pull request with a clear description of what changed and why

**Code style guidelines:**
- Vanilla JavaScript only in `pwa/app.js` — no frameworks, no npm
- `tkinter` only for dialog windows — no Qt, wxPython, or Electron
- `threading` for concurrency — not `asyncio` (pystray is not async-compatible on Windows)
- All file paths must use `base_path()` from `config.py` for frozen exe compatibility

> ⚠️ **Do not commit `servers.yaml` under any circumstances.** Pull requests containing real IP addresses or network topology will be closed immediately.

---

## License

MIT License

Copyright (c) 2026 Vistiqx Holdings LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Acknowledgements

- [homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons) — application logo CDN used for PWA tiles
- [pystray](https://github.com/moses-palmer/pystray) — Windows system tray integration
- [PyInstaller](https://pyinstaller.org) — single-file standalone exe packaging
- [Pillow](https://python-pillow.org) — programmatic icon generation
- [PyYAML](https://pyyaml.org) — YAML configuration file parsing
- [requests](https://requests.readthedocs.io) — HTTP health check requests

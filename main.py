import atexit
import ctypes
import os
import subprocess
import shutil
import sys
import tempfile
import threading
import time
import traceback
import webbrowser
from functools import partial
from urllib.parse import urlparse

import pystray
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem

import config as config_store
import health
from server import start_server


LOCK_FILE = os.path.join(tempfile.gettempdir(), "shipyard.lock")
LOG_FILE = os.path.join(tempfile.gettempdir(), "shipyard.log")
MUTEX_NAME = "Global\\ShipyardSingletonMutex"
_MUTEX_HANDLE = None


def _log(message: str) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def acquire_lock():
    global _MUTEX_HANDLE
    if os.name == "nt":
        _MUTEX_HANDLE = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == 183:
            sys.exit(0)

    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass

    with open(LOCK_FILE, "w", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    global _MUTEX_HANDLE
    if _MUTEX_HANDLE:
        ctypes.windll.kernel32.CloseHandle(_MUTEX_HANDLE)
        _MUTEX_HANDLE = None


atexit.register(release_lock)


def _asset_path(name: str) -> str:
    return os.path.join(config_store.ASSETS_PATH, name)


def _pwa_path(name: str) -> str:
    return os.path.join(config_store.base_path(), "pwa", name)


def _draw_ship_icon(path: str, alert: bool = False) -> None:
    img = Image.new("RGBA", (64, 64), "#4C3D75")
    draw = ImageDraw.Draw(img)

    # Anchor ring
    draw.ellipse((26, 4, 38, 16), outline="white", width=3)

    # Anchor shank and stock
    draw.line((32, 16, 32, 45), fill="white", width=3)
    draw.line((22, 22, 42, 22), fill="white", width=3)

    # Anchor arms
    draw.arc((14, 30, 32, 56), start=190, end=320, fill="white", width=3)
    draw.arc((32, 30, 50, 56), start=220, end=350, fill="white", width=3)

    # Flukes (tips)
    draw.polygon([(15, 49), (23, 46), (20, 55)], outline="white", fill=None)
    draw.polygon([(49, 49), (41, 46), (44, 55)], outline="white", fill=None)

    if alert:
        draw.ellipse((48, 48, 62, 62), fill="#E24B4A")

    img.save(path, format="PNG")


def _draw_pwa_icon(path: str, size: int) -> None:
    img = Image.new("RGBA", (size, size), "#4C3D75")
    draw = ImageDraw.Draw(img)
    scale = size / 64.0

    def s(value: int) -> int:
        return int(value * scale)

    color = "#AC8FFE"
    draw.ellipse((s(26), s(4), s(38), s(16)), outline=color, width=max(2, s(3)))
    draw.line((s(32), s(16), s(32), s(45)), fill=color, width=max(2, s(3)))
    draw.line((s(22), s(22), s(42), s(22)), fill=color, width=max(2, s(3)))
    draw.arc((s(14), s(30), s(32), s(56)), start=190, end=320, fill=color, width=max(2, s(3)))
    draw.arc((s(32), s(30), s(50), s(56)), start=220, end=350, fill=color, width=max(2, s(3)))
    draw.polygon([(s(15), s(49)), (s(23), s(46)), (s(20), s(55))], outline=color, fill=None)
    draw.polygon([(s(49), s(49)), (s(41), s(46)), (s(44), s(55))], outline=color, fill=None)
    img.save(path, format="PNG")


def _copy_or_resize_png(source_path: str, target_path: str, size: int | None = None) -> None:
    if not os.path.exists(source_path):
        return
    if size is None:
        shutil.copyfile(source_path, target_path)
        return
    img = Image.open(source_path).convert("RGBA")
    if img.size != (size, size):
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    img.save(target_path, format="PNG")


def _build_alert_icon(base_icon_path: str, alert_icon_path: str) -> None:
    if not os.path.exists(base_icon_path):
        return
    img = Image.open(base_icon_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    draw.ellipse((width - 16, height - 16, width - 2, height - 2), fill="#E24B4A")
    img.save(alert_icon_path, format="PNG")


def ensure_icons() -> None:
    assets_dir = config_store.ASSETS_PATH
    os.makedirs(assets_dir, exist_ok=True)

    icon_png = os.path.join(assets_dir, "icon.png")
    icon_alert_png = os.path.join(assets_dir, "icon_alert.png")
    icon_ico = os.path.join(assets_dir, "icon.ico")

    tray_source = os.path.join(assets_dir, "shipyard-tray-64.png")
    master_source = os.path.join(assets_dir, "shipyard-master-256.png")
    maskable_192_source = os.path.join(assets_dir, "shipyard-maskable-192.png")
    maskable_512_source = os.path.join(assets_dir, "shipyard-maskable-512.png")

    if os.path.exists(tray_source):
        _copy_or_resize_png(tray_source, icon_png, 64)
    elif not os.path.exists(icon_png):
        _draw_ship_icon(icon_png, alert=False)

    _build_alert_icon(icon_png, icon_alert_png)
    if not os.path.exists(icon_alert_png):
        _draw_ship_icon(icon_alert_png, alert=True)

    if os.path.exists(master_source):
        img = Image.open(master_source).convert("RGBA")
        img.save(icon_ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    elif os.path.exists(icon_png):
        img = Image.open(icon_png)
        img.save(icon_ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    pwa_dir = os.path.join(config_store.base_path(), "pwa")
    os.makedirs(pwa_dir, exist_ok=True)
    icon_192 = os.path.join(pwa_dir, "icon-192.png")
    icon_512 = os.path.join(pwa_dir, "icon-512.png")
    if os.path.exists(maskable_192_source):
        _copy_or_resize_png(maskable_192_source, icon_192, 192)
    elif os.path.exists(maskable_512_source):
        _copy_or_resize_png(maskable_512_source, icon_192, 192)
    else:
        _draw_pwa_icon(icon_192, 192)

    if os.path.exists(maskable_512_source):
        _copy_or_resize_png(maskable_512_source, icon_512, 512)
    elif os.path.exists(maskable_192_source):
        _copy_or_resize_png(maskable_192_source, icon_512, 512)
    else:
        _draw_pwa_icon(icon_512, 512)


def _status_symbol(status: str) -> str:
    return {"green": "●", "amber": "◑", "red": "○", "unknown": "·"}.get(status, "·")


def _hostname_from_url(url: str) -> str:
    raw = url.strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    if parsed.netloc:
        return parsed.netloc
    if raw.startswith("http://"):
        return raw[len("http://") :].split("/", 1)[0]
    if raw.startswith("https://"):
        return raw[len("https://") :].split("/", 1)[0]
    return raw.split("/", 1)[0]


def _any_red(config_data: dict) -> bool:
    for server in config_data.get("servers", []):
        for app in server.get("applications", []):
            if not app.get("enabled", True):
                continue
            if health.get_status(app) == "red":
                return True
    return False


def _status_snapshot(config_data: dict) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for server in config_data.get("servers", []):
        for app in server.get("applications", []):
            snapshot[config_store.get_endpoint_key(app)] = health.get_status(app)
    return snapshot


def build_menu(icon: pystray.Icon, config_data: dict, statuses: dict[str, str]) -> Menu:
    items = [
        MenuItem("↺  Refresh health checks", lambda _i, _item: refresh_health(icon)),
        MenuItem("＋  Add application...", lambda _i, _item: open_add_application(icon)),
        MenuItem("⚙  Settings...", lambda _i, _item: open_settings(icon)),
        MenuItem("?  Help & documentation", lambda _i, _item: open_help()),
        Menu.SEPARATOR,
    ]

    for server in config_data.get("servers", []):
        server_name = server.get("name", "Unnamed Server")
        app_items = []
        for app in server.get("applications", []):
            ip = str(app.get("ip", ""))
            port = int(app.get("port", 80))
            status = statuses.get(config_store.get_endpoint_key(app), "unknown")
            symbol = _status_symbol(status)
            protocol = str(app.get("protocol", "http")).lower()
            enabled = bool(app.get("enabled", True))
            app_url = config_store.get_url(app)
            raw_url = str(app.get("url", "")).strip()
            endpoint = _hostname_from_url(raw_url) if raw_url else f"{ip}:{port}"
            label = f"{symbol}  {app.get('name', 'Unnamed')}  {endpoint}"

            clickable = enabled and app_url is not None
            if not enabled:
                label = f"{label}  (disabled)"
            elif app_url is None:
                label = f"{label}  ({protocol.upper()} - not browser accessible)"

            if clickable:
                app_items.append(MenuItem(label, partial(_open_app, target=app.copy())))
            else:
                app_items.append(MenuItem(label, lambda _i, _item: None, enabled=False))

        if not app_items:
            app_items.append(MenuItem("·  No enabled applications", lambda _i, _item: None, enabled=False))

        items.append(MenuItem(server_name, Menu(*app_items)))

    items.extend([Menu.SEPARATOR, MenuItem("Quit", lambda i, _item: i.stop())])
    return Menu(*items)


def _dynamic_menu_items(icon: pystray.Icon):
    config_data = config_store.load_config()
    statuses = _status_snapshot(config_data)
    menu = build_menu(icon, config_data, statuses)
    return iter(menu.items)


def _set_tooltip(icon: pystray.Icon, config_data: dict) -> None:
    servers_count = len(config_data.get("servers", []))
    apps_count = sum(len(server.get("applications", [])) for server in config_data.get("servers", []))
    icon.title = f"Shipyard — {apps_count} applications across {servers_count} servers"


def _open_app(_icon: pystray.Icon, _item: MenuItem, target: dict) -> None:
    url = config_store.get_url(target)
    if url:
        webbrowser.open(url)


def refresh_ui(icon: pystray.Icon) -> None:
    config_data = config_store.load_config()
    icon.icon = Image.open(_asset_path("icon_alert.png" if _any_red(config_data) else "icon.png"))
    _set_tooltip(icon, config_data)
    icon.update_menu()


def refresh_health(icon: pystray.Icon) -> None:
    config_data = config_store.load_config()
    health.run_health_checks(config_data, callback=lambda: refresh_ui(icon))


def open_add_application(icon: pystray.Icon) -> None:
    webbrowser.open("http://127.0.0.1:9999#add")
    _focus_pwa_window()


def open_settings(icon: pystray.Icon) -> None:
    webbrowser.open("http://127.0.0.1:9999#settings")
    _focus_pwa_window()


def open_help() -> None:
    webbrowser.open("http://127.0.0.1:9999#help")
    _focus_pwa_window()


def _focus_pwa_window() -> None:
    try:
        subprocess.run(
            [
                "powershell",
                "-WindowStyle",
                "Hidden",
                "-Command",
                "(New-Object -ComObject Shell.Application).Windows() | "
                "Where-Object {$_.LocationURL -like '*127.0.0.1:9999*'} | "
                "ForEach-Object {$_.Visible=$true; [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($_)}",
            ],
            capture_output=True,
            timeout=3,
        )
    except Exception:
        pass


def schedule_health_checks(icon: pystray.Icon, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        cfg = config_store.load_config()
        interval = int(cfg.get("settings", {}).get("health_check_interval_seconds", 60))
        interval = max(10, interval)
        health.run_health_checks(cfg, callback=lambda: refresh_ui(icon))
        stop_event.wait(interval)


def main() -> None:
    acquire_lock()
    _log("Shipyard start")
    ensure_icons()

    config_path = config_store.get_config_path()
    first_run = not os.path.exists(config_path)

    initial_config = config_store.load_config()

    if first_run and not os.environ.get("SHIPYARD_CONFIG"):
        import tkinter.messagebox as mb

        mb.showinfo(
            "Welcome to Shipyard",
            f"Shipyard has created a configuration file at:\n\n"
            f"{config_path}\n\n"
            f"Please edit this file to add your servers and\n"
            f"applications, then restart Shipyard.\n\n"
            f"The file will now open in Notepad.",
        )
        subprocess.Popen(["notepad.exe", config_path])

    start_server(initial_config)

    if initial_config.get("settings", {}).get("pwa_first_run", True):
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:9999")
        initial_config.setdefault("settings", {})["pwa_first_run"] = False
        config_store.save_config(initial_config)

    icon_image = Image.open(_asset_path("icon.png"))
    icon = pystray.Icon("shipyard", icon_image, title="Shipyard")
    icon.menu = Menu(lambda: _dynamic_menu_items(icon))
    _set_tooltip(icon, initial_config)
    _log("Tray icon initialized")

    stop_event = threading.Event()

    def _on_setup(_icon: pystray.Icon) -> None:
        _log("Tray setup callback entered")
        try:
            _icon.visible = True
            _log("Tray icon visibility set true")
        except Exception:
            _log("Failed to force tray icon visibility")

        refresh_health(icon)
        thread = threading.Thread(target=schedule_health_checks, args=(icon, stop_event), daemon=True)
        thread.start()
        _log("Health scheduler started")
        try:
            _icon.notify("Shipyard is running in the system tray.", "Shipyard")
            _log("Startup notification sent")
        except Exception:
            _log("Startup notification unavailable")

    original_stop = icon.stop

    def _stop_wrapper() -> None:
        stop_event.set()
        original_stop()

    icon.stop = _stop_wrapper
    _log("Entering icon.run")
    icon.run(setup=_on_setup)
    _log("Exited icon.run")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        with open(LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write("\n=== Shipyard crash ===\n")
            handle.write(traceback.format_exc())
        raise

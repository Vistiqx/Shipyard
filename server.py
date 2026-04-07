import json
import os
import sys
import threading
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import config as config_store
import health
from ui.settings_dialog import set_startup


HOST = "127.0.0.1"
PORT = 9999

_SERVER_THREAD: threading.Thread | None = None
_HTTPD: ThreadingHTTPServer | None = None
_LAST_CHECK_UTC: str | None = None
_STATE_LOCK = threading.Lock()
_LOG_FILE = os.path.join(tempfile.gettempdir(), "shipyard_server.log")


def _log(message: str) -> None:
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write(f"{message}\n")
    except Exception:
        pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _set_last_check() -> None:
    global _LAST_CHECK_UTC
    with _STATE_LOCK:
        _LAST_CHECK_UTC = _utc_now_iso()


def _get_last_check() -> str | None:
    with _STATE_LOCK:
        return _LAST_CHECK_UTC


def _pwa_dir() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(getattr(sys, "_MEIPASS"), "pwa")
    return os.path.join(config_store.base_path(), "pwa")


def _status_payload() -> dict:
    cfg = config_store.load_config()
    servers_out = []

    total = 0
    enabled_count = 0
    green = amber = red = unknown = 0

    for server in cfg.get("servers", []):
        apps_out = []
        for app in server.get("applications", []):
            total += 1
            is_enabled = bool(app.get("enabled", True))
            protocol = str(app.get("protocol", "http")).lower()
            url = config_store.get_url(app)
            clickable = is_enabled and protocol in {"http", "https"} and url is not None

            status = "unknown"
            if is_enabled and clickable:
                status = health.get_status(str(app.get("ip", "")), int(app.get("port", 80)))

            if is_enabled:
                enabled_count += 1
                if status == "green":
                    green += 1
                elif status == "amber":
                    amber += 1
                elif status == "red":
                    red += 1
                else:
                    unknown += 1

            apps_out.append(
                {
                    "name": app.get("name"),
                    "ip": app.get("ip"),
                    "port": app.get("port"),
                    "protocol": protocol,
                    "path": app.get("path", ""),
                    "url": url,
                    "enabled": is_enabled,
                    "status": status,
                    "clickable": clickable,
                }
            )
        servers_out.append({"name": server.get("name", "Unnamed Server"), "applications": apps_out})

    return {
        "servers": servers_out,
        "summary": {
            "total": total,
            "enabled": enabled_count,
            "green": green,
            "amber": amber,
            "red": red,
            "unknown": unknown,
            "last_check": _get_last_check(),
        },
    }


def _kick_health_check(config_data: dict | None = None) -> None:
    cfg = config_data or config_store.load_config()
    health.run_health_checks(cfg, callback=_set_last_check)


class ShipyardHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:9999")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: str, content_type: str) -> None:
        if not os.path.exists(file_path):
            self.send_error(404)
            return
        with open(file_path, "rb") as handle:
            data = handle.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:9999")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        try:
            path = urlparse(self.path).path
            if path == "/api/status":
                self._send_json(_status_payload())
                return
            if path == "/api/config":
                self._send_json(config_store.load_config())
                return

            static_map = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/manifest.json": ("manifest.json", "application/json; charset=utf-8"),
                "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
                "/app.js": ("app.js", "application/javascript; charset=utf-8"),
                "/icon-192.png": ("icon-192.png", "image/png"),
                "/icon-512.png": ("icon-512.png", "image/png"),
            }
            if path in static_map:
                file_name, mime = static_map[path]
                self._send_file(os.path.join(_pwa_dir(), file_name), mime)
                return

            self.send_error(404)
        except Exception as exc:
            _log(f"GET {self.path} failed: {exc}")
            self._send_json({"status": "error", "message": str(exc)}, status=500)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_json_body()

            if path == "/api/refresh":
                _kick_health_check()
                self._send_json({"status": "ok", "message": "Health check started"})
                return

            if path == "/api/application/add":
                required = ["server_name", "name", "ip", "port", "protocol", "enabled"]
                for key in required:
                    if key not in body:
                        self._send_json({"status": "error", "message": f"Missing field: {key}"}, status=400)
                        return
                app = {
                    "name": body["name"],
                    "ip": body["ip"],
                    "port": int(body["port"]),
                    "protocol": str(body["protocol"]).lower(),
                    "path": body.get("path", ""),
                    "enabled": bool(body.get("enabled", True)),
                }
                config_store.add_application(body["server_name"], app)

                target_cfg = {
                    "settings": config_store.load_config().get("settings", {}),
                    "servers": [{"name": body["server_name"], "applications": [app]}],
                }
                _kick_health_check(target_cfg)
                self._send_json({"status": "ok"})
                return

            if path == "/api/application/edit":
                required = ["original_name", "original_server", "server_name", "name", "ip", "port", "protocol", "enabled"]
                for key in required:
                    if key not in body:
                        self._send_json({"status": "error", "message": f"Missing field: {key}"}, status=400)
                        return

                cfg = config_store.load_config()
                found = False
                for server in cfg.get("servers", []):
                    if server.get("name") != body["original_server"]:
                        continue
                    for idx, app in enumerate(server.get("applications", [])):
                        if app.get("name") == body["original_name"]:
                            del server["applications"][idx]
                            found = True
                            break
                    if found:
                        break

                if not found:
                    self._send_json({"status": "error", "message": "Original application not found"}, status=404)
                    return

                target_server = next((s for s in cfg.get("servers", []) if s.get("name") == body["server_name"]), None)
                if target_server is None:
                    self._send_json({"status": "error", "message": "Target server not found"}, status=404)
                    return

                target_server.setdefault("applications", []).append(
                    {
                        "name": body["name"],
                        "ip": body["ip"],
                        "port": int(body["port"]),
                        "protocol": str(body["protocol"]).lower(),
                        "path": body.get("path", ""),
                        "enabled": bool(body.get("enabled", True)),
                    }
                )
                config_store.save_config(cfg)
                _kick_health_check()
                self._send_json({"status": "ok"})
                return

            if path == "/api/application/remove":
                config_store.remove_application(body.get("server_name", ""), body.get("name", ""))
                _kick_health_check()
                self._send_json({"status": "ok"})
                return

            if path == "/api/application/toggle":
                config_store.toggle_application(body.get("server_name", ""), body.get("name", ""), bool(body.get("enabled")))
                _kick_health_check()
                self._send_json({"status": "ok"})
                return

            if path == "/api/server/add":
                config_store.add_server(str(body.get("name", "")))
                self._send_json({"status": "ok"})
                return

            if path == "/api/server/remove":
                name = str(body.get("name", "")).strip()
                cfg = config_store.load_config()
                cfg["servers"] = [s for s in cfg.get("servers", []) if s.get("name") != name]
                config_store.save_config(cfg)
                _kick_health_check()
                self._send_json({"status": "ok"})
                return

            if path == "/api/settings/update":
                cfg = config_store.load_config()
                settings = cfg.setdefault("settings", {})
                prev_startup = bool(settings.get("launch_at_startup", False))
                settings["launch_at_startup"] = bool(body.get("launch_at_startup", prev_startup))
                settings["health_check_interval_seconds"] = int(body.get("health_check_interval_seconds", settings.get("health_check_interval_seconds", 60)))
                settings["health_check_timeout_seconds"] = int(body.get("health_check_timeout_seconds", settings.get("health_check_timeout_seconds", 5)))
                config_store.save_config(cfg)
                if prev_startup != settings["launch_at_startup"]:
                    set_startup(settings["launch_at_startup"])
                _kick_health_check()
                self._send_json({"status": "ok"})
                return

            self._send_json({"status": "error", "message": "Not found"}, status=404)
        except Exception as exc:
            self._send_json({"status": "error", "message": str(exc)}, status=500)


def start_server(_config: dict | None = None) -> None:
    global _SERVER_THREAD, _HTTPD
    if _SERVER_THREAD and _SERVER_THREAD.is_alive():
        return

    _HTTPD = ThreadingHTTPServer((HOST, PORT), ShipyardHandler)
    _log(f"Server listening on {HOST}:{PORT}, pwa_dir={_pwa_dir()}")

    def _run() -> None:
        _HTTPD.serve_forever(poll_interval=0.5)

    _SERVER_THREAD = threading.Thread(target=_run, daemon=True)
    _SERVER_THREAD.start()

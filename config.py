import copy
import os
import shutil
import sys
from typing import Any

import yaml


DEFAULT_CONFIG_YAML = """settings:
  pwa_first_run: true
  launch_at_startup: true
  health_check_interval_seconds: 60
  health_check_timeout_seconds: 5
  default_protocol: http

servers:
  - name: MY-SERVER
    applications:
      - name: My Application
        ip: 10.0.0.10
        port: 8080
        protocol: http
        path: ""
        enabled: true
"""


MINIMAL_DEFAULT_CONFIG = {
    'settings': {
        'pwa_first_run': True,
        'launch_at_startup': True,
        'health_check_interval_seconds': 60,
        'health_check_timeout_seconds': 5,
        'default_protocol': 'http'
    },
    'servers': [
        {
            'name': 'MY-SERVER',
            'applications': [
                {
                    'name': 'My Application',
                    'ip': '10.0.0.10',
                    'port': 8080,
                    'protocol': 'http',
                    'path': '',
                    'enabled': True
                }
            ]
        }
    ]
}


DEFAULT_CONFIG: dict[str, Any] = MINIMAL_DEFAULT_CONFIG


def base_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_config_path() -> str:
    override = os.environ.get("SHIPYARD_CONFIG")
    if override and os.path.exists(override):
        return override
    return os.path.join(base_path(), "config", "servers.yaml")


CONFIG_PATH = get_config_path()
TEMPLATE_PATH = os.path.join(base_path(), "config", "servers.yaml.template")
ASSETS_PATH = os.path.join(base_path(), "assets")


def write_minimal_default_config(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(copy.deepcopy(DEFAULT_CONFIG), handle, sort_keys=False, allow_unicode=True)


def _normalize_app(app: dict[str, Any], default_protocol: str) -> dict[str, Any]:
    protocol = str(app.get("protocol", default_protocol)).strip().lower()
    if protocol not in {"http", "https", "tcp", "udp"}:
        protocol = default_protocol

    path = app.get("path", "")
    if path is None:
        path = ""
    path = str(path)
    if protocol in {"http", "https"} and path and not path.startswith("/"):
        path = f"/{path}"

    return {
        "name": str(app.get("name", "Unnamed App")).strip() or "Unnamed App",
        "ip": str(app.get("ip", "")).strip(),
        "port": int(app.get("port", 80)),
        "protocol": protocol,
        "path": path,
        "enabled": bool(app.get("enabled", True)),
    }


def _normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(DEFAULT_CONFIG)

    settings = config.get("settings", {}) if isinstance(config.get("settings"), dict) else {}
    base_settings = base["settings"]
    base_settings["pwa_first_run"] = bool(settings.get("pwa_first_run", base_settings["pwa_first_run"]))
    base_settings["launch_at_startup"] = bool(settings.get("launch_at_startup", base_settings["launch_at_startup"]))
    base_settings["health_check_interval_seconds"] = max(
        10, int(settings.get("health_check_interval_seconds", base_settings["health_check_interval_seconds"]))
    )
    base_settings["health_check_timeout_seconds"] = max(
        1, min(30, int(settings.get("health_check_timeout_seconds", base_settings["health_check_timeout_seconds"])))
    )
    default_protocol = str(settings.get("default_protocol", base_settings["default_protocol"])).strip().lower()
    if default_protocol not in {"http", "https", "tcp", "udp"}:
        default_protocol = "http"
    base_settings["default_protocol"] = default_protocol

    servers_in = config.get("servers", []) if isinstance(config.get("servers"), list) else []
    servers_out: list[dict[str, Any]] = []
    for server in servers_in:
        if not isinstance(server, dict):
            continue
        name = str(server.get("name", "Unnamed Server")).strip() or "Unnamed Server"
        apps_in = server.get("applications", []) if isinstance(server.get("applications"), list) else []
        apps_out = [_normalize_app(app, default_protocol) for app in apps_in if isinstance(app, dict)]
        servers_out.append({"name": name, "applications": apps_out})

    base["servers"] = servers_out
    return base


def load_config() -> dict[str, Any]:
    config_path = os.environ.get("SHIPYARD_CONFIG") or get_config_path()
    template_path = TEMPLATE_PATH

    if not os.path.exists(config_path):
        if os.environ.get("SHIPYARD_CONFIG"):
            raise FileNotFoundError(
                f"SHIPYARD_CONFIG is set to {config_path} but file does not exist."
            )
        if os.path.exists(template_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            shutil.copy(template_path, config_path)
        else:
            write_minimal_default_config(config_path)
        return load_config()

    with open(config_path, "r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}

    if not isinstance(loaded, dict):
        raise ValueError("servers.yaml must contain a YAML mapping at root")

    return _normalize_config(loaded)


def save_config(config: dict[str, Any]) -> None:
    path = os.environ.get("SHIPYARD_CONFIG") or get_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    normalized = _normalize_config(config)
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(normalized, handle, sort_keys=False, allow_unicode=True)


def get_url(app: dict[str, Any]) -> str | None:
    protocol = str(app.get("protocol", "http")).strip().lower()
    if protocol not in {"http", "https"}:
        return None

    ip = str(app.get("ip", "")).strip()
    port = int(app.get("port", 80))
    path = app.get("path", "")
    if path is None or path == "":
        return f"{protocol}://{ip}:{port}"
    path = str(path)
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{protocol}://{ip}:{port}{path}"


def add_server(name: str) -> None:
    config = load_config()
    config.setdefault("servers", []).append({"name": name.strip() or "Unnamed Server", "applications": []})
    save_config(config)


def add_application(server_name: str, app: dict[str, Any]) -> None:
    config = load_config()
    default_protocol = config.get("settings", {}).get("default_protocol", "http")
    normalized_app = _normalize_app(app, str(default_protocol))
    for server in config.get("servers", []):
        if server.get("name") == server_name:
            server.setdefault("applications", []).append(normalized_app)
            save_config(config)
            return
    raise ValueError(f"Server not found: {server_name}")


def remove_application(server_name: str, app_name: str) -> None:
    config = load_config()
    for server in config.get("servers", []):
        if server.get("name") != server_name:
            continue
        server["applications"] = [app for app in server.get("applications", []) if app.get("name") != app_name]
        save_config(config)
        return
    raise ValueError(f"Server not found: {server_name}")


def toggle_application(server_name: str, app_name: str, enabled: bool) -> None:
    config = load_config()
    for server in config.get("servers", []):
        if server.get("name") != server_name:
            continue
        for app in server.get("applications", []):
            if app.get("name") == app_name:
                app["enabled"] = bool(enabled)
                save_config(config)
                return
        raise ValueError(f"Application not found: {app_name}")
    raise ValueError(f"Server not found: {server_name}")

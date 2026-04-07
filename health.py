import threading
from typing import Any, Callable

import requests
import urllib3

from config import get_url


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_STATUS_CACHE: dict[str, str] = {}
_CACHE_LOCK = threading.Lock()


def _cache_key(ip: str, port: int) -> str:
    return f"{ip}:{port}"


def get_status(ip: str, port: int) -> str:
    with _CACHE_LOCK:
        return _STATUS_CACHE.get(_cache_key(ip, port), "unknown")


def _set_status(ip: str, port: int, status: str) -> None:
    with _CACHE_LOCK:
        _STATUS_CACHE[_cache_key(ip, port)] = status


def _classify_exception(exc: Exception) -> str:
    text = str(exc).lower()
    if "timed out" in text or "timeout" in text or "no route to host" in text:
        return "red"
    if (
        "connection refused" in text
        or "actively refused" in text
        or "winerror 10061" in text
        or "[errno 111]" in text
    ):
        return "amber"
    return "red"


def _check_server_apps(apps: list[dict[str, Any]], timeout_seconds: int) -> None:
    with requests.Session() as session:
        session.verify = False
        for app in apps:
            if not app.get("enabled", True):
                continue

            ip = str(app.get("ip", ""))
            port = int(app.get("port", 80))
            url = get_url(app)
            if not url:
                _set_status(ip, port, "unknown")
                continue

            try:
                response = session.get(url, timeout=timeout_seconds)
                if 200 <= response.status_code <= 399:
                    _set_status(ip, port, "green")
                elif 400 <= response.status_code <= 599:
                    _set_status(ip, port, "amber")
                else:
                    _set_status(ip, port, "red")
            except requests.exceptions.Timeout as exc:
                _set_status(ip, port, _classify_exception(exc))
            except requests.exceptions.ConnectionError as exc:
                _set_status(ip, port, _classify_exception(exc))
            except requests.RequestException as exc:
                _set_status(ip, port, _classify_exception(exc))


def run_health_checks(config: dict[str, Any], callback: Callable[[], None] | None = None) -> None:
    timeout_seconds = int(config.get("settings", {}).get("health_check_timeout_seconds", 5))
    timeout_seconds = max(1, min(30, timeout_seconds))

    def _runner() -> None:
        threads: list[threading.Thread] = []
        for server in config.get("servers", []):
            apps = server.get("applications", [])
            thread = threading.Thread(target=_check_server_apps, args=(apps, timeout_seconds), daemon=True)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if callback:
            callback()

    threading.Thread(target=_runner, daemon=True).start()

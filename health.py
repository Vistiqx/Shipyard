import threading
import time
from typing import Any, Callable
from urllib.parse import urlparse

import requests
import urllib3

from config import get_endpoint_key, get_url


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_STATUS_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_LOCK = threading.Lock()


def _cache_key(app: dict[str, Any]) -> str:
    return get_endpoint_key(app)


def get_status(app: dict[str, Any]) -> str:
    with _CACHE_LOCK:
        entry = _STATUS_CACHE.get(_cache_key(app), {})
        return str(entry.get("status", "unknown"))


def get_status_details(app: dict[str, Any]) -> dict[str, Any]:
    with _CACHE_LOCK:
        entry = _STATUS_CACHE.get(_cache_key(app), {})
        return {
            "status": str(entry.get("status", "unknown")),
            "response_time_ms": entry.get("response_time_ms"),
        }


def _set_status(app: dict[str, Any], status: str, response_time_ms: int | None = None) -> None:
    with _CACHE_LOCK:
        _STATUS_CACHE[_cache_key(app)] = {
            "status": status,
            "response_time_ms": response_time_ms,
        }


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

            url = get_url(app)
            if not url:
                _set_status(app, "unknown", None)
                continue

            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                _set_status(app, "unknown", None)
                continue

            try:
                start = time.monotonic()
                response = session.get(url, timeout=timeout_seconds)
                elapsed_ms = round((time.monotonic() - start) * 1000)
                if 200 <= response.status_code <= 399:
                    _set_status(app, "green", elapsed_ms)
                elif 400 <= response.status_code <= 599:
                    _set_status(app, "amber", elapsed_ms)
                else:
                    _set_status(app, "red", elapsed_ms)
            except requests.exceptions.Timeout as exc:
                _set_status(app, _classify_exception(exc), None)
            except requests.exceptions.ConnectionError as exc:
                _set_status(app, _classify_exception(exc), None)
            except requests.RequestException as exc:
                _set_status(app, _classify_exception(exc), None)


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

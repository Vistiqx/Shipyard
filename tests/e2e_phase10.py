import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import yaml


ROOT = Path(r"D:\__Projects\Shipyard")


def get_json(path: str) -> dict:
    with urlopen(f"http://127.0.0.1:9999{path}", timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_json(path: str, payload: dict) -> dict:
    req = Request(
        f"http://127.0.0.1:9999{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run() -> dict:
    results: dict[str, tuple[str, str]] = {}

    env = os.environ.copy()
    env["SHIPYARD_CONFIG"] = str(ROOT / "config" / "servers.yaml")
    proc = subprocess.Popen(["py", "-3", str(ROOT / "main.py")], cwd=str(ROOT), env=env)

    try:
        # Wait for API
        online = False
        for _ in range(40):
            try:
                data = get_json("/api/status")
                if isinstance(data, dict):
                    online = True
                    break
            except Exception:
                time.sleep(0.5)

        if not online:
            results["T01"] = ("FAIL", "Shipyard API did not start")
            return results

        # T01
        cfg = yaml.safe_load((ROOT / "config" / "servers.yaml").read_text(encoding="utf-8"))
        all_empty = all(str(a.get("url", "")).strip() == "" for s in cfg.get("servers", []) for a in s.get("applications", []))

        sys.path.insert(0, str(ROOT))
        from config import get_url

        get_url_ok = True
        for server in cfg.get("servers", []):
            for app in server.get("applications", []):
                protocol = str(app.get("protocol", "http")).lower()
                got = get_url(app)
                if protocol in {"tcp", "udp"}:
                    if got is not None:
                        get_url_ok = False
                        break
                else:
                    ip = str(app.get("ip", "")).strip()
                    port = int(app.get("port", 0))
                    path = str(app.get("path", "")).strip()
                    expected = f"{protocol}://{ip}:{port}" + ((path if path.startswith("/") else f"/{path}") if path else "")
                    if got != expected:
                        get_url_ok = False
                        break
            if not get_url_ok:
                break

        main_src = (ROOT / "main.py").read_text(encoding="utf-8")
        pwa_src = (ROOT / "pwa" / "app.js").read_text(encoding="utf-8")
        tray_check = "endpoint = _hostname_from_url(raw_url) if raw_url else f\"{ip}:{port}\"" in main_src
        pwa_check = "if (app.raw_url)" in pwa_src and "port-badge" in pwa_src
        results["T01"] = ("PASS", "Backward compatibility verified") if (all_empty and get_url_ok and tray_check and pwa_check) else (
            "FAIL",
            f"all_empty={all_empty}, get_url_ok={get_url_ok}, tray={tray_check}, pwa={pwa_check}",
        )

        # T02
        try:
            app1 = {"url": "https://nextcloud.mydomain.com", "ip": "10.20.1.222", "port": 8080, "protocol": "http", "path": ""}
            assert get_url(app1) == "https://nextcloud.mydomain.com"
            print("T02.1 PASS: url field takes precedence over ip+port")

            app2 = {"url": "", "ip": "10.20.1.218", "port": 5678, "protocol": "http", "path": ""}
            assert get_url(app2) == "http://10.20.1.218:5678"
            print("T02.2 PASS: empty url uses ip+port correctly")

            app3 = {"url": "https://pihole.mydomain.com/admin", "ip": "", "port": 0, "protocol": "https", "path": ""}
            assert get_url(app3) == "https://pihole.mydomain.com/admin"
            print("T02.3 PASS: url with path works correctly")

            app4 = {"url": "", "ip": "10.20.1.201", "port": 5432, "protocol": "tcp", "path": ""}
            assert get_url(app4) is None
            print("T02.4 PASS: tcp protocol returns None")

            app5 = {"ip": "10.20.1.222", "port": 8080, "protocol": "http", "path": ""}
            assert get_url(app5) == "http://10.20.1.222:8080"
            print("T02.5 PASS: missing url key handled gracefully")
            print("T02 ALL PASS")
            results["T02"] = ("PASS", "get_url tests passed")
        except AssertionError as exc:
            results["T02"] = ("FAIL", str(exc))

        # T03
        status = get_json("/api/status")
        t03_ok = True
        for s in status.get("servers", []):
            for a in s.get("applications", []):
                if "url" not in a or "raw_url" not in a:
                    t03_ok = False
                if str(a.get("protocol", "")).lower() in {"tcp", "udp"} and a.get("url") is not None:
                    t03_ok = False
        results["T03"] = ("PASS", "status includes url/raw_url fields") if t03_ok else ("FAIL", "status field validation failed")

        # T04
        add_resp = post_json(
            "/api/application/add",
            {
                "server_name": "TALOS-APPS",
                "name": "Test Proxied App",
                "ip": "",
                "port": 0,
                "protocol": "https",
                "path": "",
                "url": "https://test.example.com",
                "enabled": True,
            },
        )
        status2 = get_json("/api/status")
        found = None
        for s in status2.get("servers", []):
            for a in s.get("applications", []):
                if a.get("name") == "Test Proxied App":
                    found = a
                    break
        import main
        import config as config_store

        cfg2 = config_store.load_config()
        menu = main.build_menu(None, cfg2, main._status_snapshot(cfg2))
        labels = []
        for item in menu.items:
            if getattr(item, "submenu", None) is not None:
                for sub in item.submenu.items:
                    labels.append(getattr(sub, "text", ""))
        tray_host = any("Test Proxied App" in x and "test.example.com" in x for x in labels)
        t04_ok = add_resp.get("status") == "ok" and found is not None and found.get("url") == "https://test.example.com" and tray_host
        results["T04"] = ("PASS", "proxied app add + status + tray hostname verified") if t04_ok else (
            "FAIL",
            f"add_resp={add_resp}, found={found}, tray_host={tray_host}",
        )

        # T05
        rm_resp = post_json("/api/application/remove", {"server_name": "TALOS-APPS", "name": "Test Proxied App"})
        status3 = get_json("/api/status")
        still = any(a.get("name") == "Test Proxied App" for s in status3.get("servers", []) for a in s.get("applications", []))
        t05_ok = rm_resp.get("status") == "ok" and not still
        results["T05"] = ("PASS", "test app removed") if t05_ok else ("FAIL", f"rm_resp={rm_resp}, still={still}")

        # T06
        appjs = (ROOT / "pwa" / "app.js").read_text(encoding="utf-8")
        html = (ROOT / "pwa" / "index.html").read_text(encoding="utf-8")
        c1 = "if (app.raw_url)" in appjs and "proxy-badge" in appjs and "hostnameFromUrl(app.raw_url)" in appjs
        c2 = "port-badge" in appjs
        c3 = ".proxy-badge {" in html and "color: #5DCAA5;" in html and "border: 1px solid #1D9E75;" in html
        results["T06"] = ("PASS", "PWA badge rendering paths verified") if (c1 and c2 and c3) else (
            "FAIL",
            f"c1={c1}, c2={c2}, c3={c3}",
        )

        # T07
        tpl = (ROOT / "config" / "servers.yaml.template").read_text(encoding="utf-8")
        has_schema = "url:        Optional. Full URL including protocol, hostname, and path." in tpl
        has_examples = "name: My Direct Application" in tpl and "name: My Proxied Application" in tpl
        no_real_ip = "10.20." not in tpl
        no_real_domain = "test.example.com" not in tpl
        t07_ok = has_schema and has_examples and no_real_ip and no_real_domain
        results["T07"] = ("PASS", "servers.yaml.template verified") if t07_ok else (
            "FAIL",
            f"schema={has_schema}, examples={has_examples}, no_real_ip={no_real_ip}, no_real_domain={no_real_domain}",
        )

    finally:
        try:
            proc.terminate()
            time.sleep(1)
            if proc.poll() is None:
                proc.kill()
        except Exception:
            pass

    # T08
    test_dir = Path(r"C:\ShipyardTest")
    if test_dir.exists():
        subprocess.run(["powershell", "-Command", f"Remove-Item -LiteralPath '{test_dir}' -Recurse -Force"], check=False)
    test_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "powershell",
            "-Command",
            f"Copy-Item -LiteralPath '{ROOT / 'dist' / 'shipyard.exe'}' -Destination '{test_dir / 'shipyard.exe'}' -Force",
        ],
        check=True,
    )

    exe_proc = subprocess.Popen([str(test_dir / "shipyard.exe")], cwd=str(test_dir))
    cfg_path = test_dir / "config" / "servers.yaml"
    cfg_created = False
    for _ in range(30):
        if cfg_path.exists():
            cfg_created = True
            break
        time.sleep(1)
    cfg_has_url = cfg_created and ("url:" in cfg_path.read_text(encoding="utf-8", errors="ignore"))
    alive = exe_proc.poll() is None

    try:
        exe_proc.terminate()
        time.sleep(1)
        if exe_proc.poll() is None:
            exe_proc.kill()
    except Exception:
        pass
    subprocess.run(["powershell", "-Command", f"Remove-Item -LiteralPath '{test_dir}' -Recurse -Force"], check=False)

    t08_ok = cfg_created and cfg_has_url and alive
    results["T08"] = ("PASS", "exe first-run smoke checks passed") if t08_ok else (
        "FAIL",
        f"cfg_created={cfg_created}, cfg_has_url={cfg_has_url}, alive={alive}",
    )

    return results


if __name__ == "__main__":
    out = run()
    for key in [f"T0{i}" for i in range(1, 9)]:
        status, msg = out.get(key, ("FAIL", "Not executed"))
        print(f"{key} {status}: {msg}")
    (ROOT / "URL_FEATURE_TEST_RESULTS.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

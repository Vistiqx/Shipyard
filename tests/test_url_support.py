import unittest

import config
import health


class UrlSupportTests(unittest.TestCase):
    def test_normalize_app_sets_url_default(self) -> None:
        app = config._normalize_app(
            {
                "name": "Example",
                "ip": "10.0.0.10",
                "port": 8080,
                "protocol": "http",
                "path": "",
                "enabled": True,
            },
            "http",
        )
        self.assertEqual(app["url"], "")

    def test_get_url_prefers_explicit_url(self) -> None:
        app = {
            "ip": "10.0.0.10",
            "port": 8080,
            "protocol": "http",
            "path": "/ignored",
            "url": "https://nextcloud.mydomain.com",
        }
        self.assertEqual(config.get_url(app), "https://nextcloud.mydomain.com")

    def test_get_url_falls_back_to_ip_port_path(self) -> None:
        app = {
            "ip": "10.0.0.10",
            "port": 8080,
            "protocol": "http",
            "path": "admin",
            "url": "",
        }
        self.assertEqual(config.get_url(app), "http://10.0.0.10:8080/admin")

    def test_get_url_returns_explicit_url_verbatim(self) -> None:
        app = {
            "ip": "10.0.0.10",
            "port": 8080,
            "protocol": "http",
            "path": "",
            "url": "ftp://example.com",
        }
        self.assertEqual(config.get_url(app), "ftp://example.com")

    def test_normalize_app_disables_when_url_empty_and_ip_missing(self) -> None:
        app = config._normalize_app(
            {
                "name": "Broken app",
                "ip": "",
                "port": 8080,
                "protocol": "http",
                "path": "",
                "url": "",
                "enabled": True,
            },
            "http",
        )
        self.assertFalse(app["enabled"])

    def test_normalize_app_keeps_enabled_when_url_present(self) -> None:
        app = config._normalize_app(
            {
                "name": "Proxied app",
                "ip": "",
                "port": 0,
                "protocol": "https",
                "path": "",
                "url": "https://app.example.com",
                "enabled": True,
            },
            "http",
        )
        self.assertTrue(app["enabled"])

    def test_endpoint_key_uses_url_when_present(self) -> None:
        app = {"ip": "", "port": 0, "url": "https://app.example.com"}
        self.assertEqual(config.get_endpoint_key(app), "url:https://app.example.com")

    def test_health_cache_isolated_for_different_urls(self) -> None:
        app_a = {"ip": "", "port": 0, "url": "https://a.example.com"}
        app_b = {"ip": "", "port": 0, "url": "https://b.example.com"}
        health._set_status(app_a, "green")
        self.assertEqual(health.get_status(app_a), "green")
        self.assertEqual(health.get_status(app_b), "unknown")


if __name__ == "__main__":
    unittest.main()

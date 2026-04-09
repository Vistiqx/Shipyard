HELP_TEXT = [
    ("heading", "Getting Started"),
    (
        "body",
        "Shipyard is a Windows system tray application that gives you one-click access to self-hosted services grouped by server.",
    ),
    (
        "body",
        "If you do not see the icon after launch, open the Windows notification area overflow (the ^ button near the clock) and look for Shipyard.",
    ),
    (
        "body",
        "To keep Shipyard visible, drag the icon from overflow to the taskbar tray area or enable it in Taskbar settings so it always shows.",
    ),

    ("heading", "The Tray Menu"),
    (
        "body",
        "The menu is organized by server group. Each server section contains the applications assigned to that group.",
    ),
    (
        "body",
        "Status indicators: ● reachable, ◑ degraded, ○ unreachable, · not yet checked.",
    ),
    (
        "body",
        "Greyed-out entries are TCP/UDP services with no web interface.",
    ),
    (
        "body",
        "Clicking a web application opens its UI in your default browser.",
    ),
    (
        "body",
        "The menu shows IP:port. The full URL also includes protocol and any configured path suffix.",
    ),

    ("heading", "Header Icons"),
    (
        "body",
        "↺ Refresh: immediately re-runs all health checks.",
    ),
    (
        "body",
        "＋ Add application: opens the dialog to register a new container.",
    ),
    (
        "body",
        "⚙ Settings: manage servers, applications, and preferences.",
    ),
    (
        "body",
        "? Help: opens this documentation window.",
    ),

    ("heading", "Managing Applications"),
    (
        "body",
        "Use Add, Edit, Enabled toggle, and Remove to manage application entries.",
    ),
    (
        "body",
        "Path suffix is for apps that need a sub-route (for example, Pi-hole requires /admin).",
    ),
    (
        "body",
        "Use http/https for browser-accessible web UIs. Use tcp/udp for non-browser services.",
    ),
    ("heading", "Direct URL (reverse proxy support)"),
    (
        "body",
        "Some applications are not accessed directly by IP and port — they sit behind a reverse proxy such as Traefik and are reached via a domain name URL like https://nextcloud.mydomain.com.\n"
        "For these applications, set the url field in servers.yaml instead of (or in addition to) ip and port:\n\n"
        "name: Nextcloud\n"
        "ip: \"\"\n"
        "port: 0\n"
        "protocol: https\n"
        "path: \"\"\n"
        "url: https://nextcloud.mydomain.com\n"
        "enabled: true\n\n"
        "When url is set, Shipyard uses it directly for both health checks and browser launch. The ip and port fields become optional reference information only.\n"
        "When url is empty, Shipyard builds the URL from ip + port + path exactly as before. All existing direct-IP applications continue to work without any changes.",
    ),
    (
        "body",
        "Disabled applications are hidden from the tray menu entirely.",
    ),
    (
        "body",
        "TCP/UDP applications are shown as greyed-out informational entries and are not clickable.",
    ),

    ("heading", "Managing Servers"),
    (
        "body",
        "You can add and remove server groups from Settings.",
    ),
    (
        "body",
        "Server groups are organizational only. A group itself does not require direct network access.",
    ),

    ("heading", "Configuration File"),
    (
        "body",
        "Configuration file location: config/servers.yaml in the same directory as shipyard.exe.",
    ),
    (
        "body",
        "Schema:\n"
        "settings:\n"
        "  launch_at_startup: true|false\n"
        "  health_check_interval_seconds: 10-3600\n"
        "  health_check_timeout_seconds: 1-30\n"
        "  default_protocol: http|https|tcp|udp\n"
        "servers:\n"
        "  - name: string\n"
        "    applications:\n"
        "      - name: string\n"
        "        ip: ipv4-or-hostname\n"
        "        port: integer\n"
        "        protocol: http|https|tcp|udp\n"
        "        path: string (used for http/https)\n"
        "        enabled: true|false",
    ),
    (
        "body",
        "You can safely hand-edit servers.yaml while Shipyard is not running.",
    ),
    (
        "body",
        "If the file is missing or corrupted, Shipyard regenerates it from built-in defaults.",
    ),

    ("heading", "Health Checks"),
    (
        "body",
        "Shipyard sends an HTTP GET to each enabled http/https application URL.",
    ),
    (
        "body",
        "Green: 200-399 | Amber: 400-599 or refused | Red: timeout/unreachable.",
    ),
    (
        "body",
        "TCP and UDP entries are never health-checked.",
    ),
    (
        "body",
        "Self-signed certificates are accepted for health checks.",
    ),
    (
        "body",
        "Health check interval and timeout are configurable in Settings.",
    ),

    ("heading", "Windows Startup"),
    (
        "body",
        "Enable or disable startup from Settings.",
    ),
    (
        "body",
        "Registry key used: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Shipyard.",
    ),
    (
        "body",
        "You can remove it manually with regedit if needed.",
    ),

    ("heading", "FAQ"),
    (
        "body",
        "Q: An application shows red but I know it is running. What do I do?\n"
        "A: Verify the IP and port in servers.yaml match what the container actually exposes on the host. "
        "Some applications also require a path suffix - for example Pi-hole needs /admin. "
        "You can edit these values in Settings or directly in servers.yaml.",
    ),
    (
        "body",
        "Q: Can I use hostnames instead of IP addresses?\n"
        "A: Yes. The IP field accepts any hostname or FQDN that resolves on your network.",
    ),
    (
        "body",
        "Q: I have applications behind Traefik with domain names. How do I add them?\n"
        "A: Set the url field to the full domain URL including protocol, for example https://nextcloud.mydomain.com. "
        "Leave ip and port blank or set them as optional reference. Shipyard will use the url field directly for health "
        "checks and browser launch.",
    ),
    (
        "body",
        "Q: Can I mix direct IP applications and proxied URL applications in the same config?\n"
        "A: Yes. Each application independently uses either url (if set) or ip + port. "
        "You can have both types in the same server group with no conflict.",
    ),
    (
        "body",
        "Q: How do I add HTTPS support for a self-signed certificate?\n"
        "A: Set protocol to https. Shipyard accepts self-signed certs for health checks. "
        "Your browser will show a certificate warning on first visit - accept it once and it will be remembered.",
    ),
    (
        "body",
        "Q: The tray icon does not appear after launching Shipyard.\n"
        "A: Check the Windows notification area overflow. Right-click the taskbar, open Taskbar settings, "
        "find Other system tray icons, and enable Shipyard.",
    ),
    (
        "body",
        "Q: How do I rebuild the exe after making code changes?\n"
        "A: Run pyinstaller shipyard.spec --clean from the project root.",
    ),
    (
        "body",
        "Q: Can I run multiple instances of Shipyard?\n"
        "A: No. A lock file at %TEMP%\\shipyard.lock prevents this. If Shipyard crashed without cleaning up, "
        "delete that file and relaunch.",
    ),
    (
        "body",
        "Q: Why are Postgres, Redis, Bind9, FreeRADIUS, and fmdns greyed out?\n"
        "A: These are TCP/UDP services with no browser interface. They are included in the config for inventory visibility "
        "but cannot be opened in a browser.",
    ),
]

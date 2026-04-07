import ipaddress
import tkinter as tk
from tkinter import messagebox

import config as config_store


BG = "#1E1E2E"
FG = "#E8E8F8"
ACCENT = "#AC8FFE"
BORDER = "#4C3D75"
FONT = ("Segoe UI", 10)


def _center_window(window: tk.Toplevel, width: int, height: int) -> None:
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def _valid_host(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    try:
        ipaddress.IPv4Address(value)
        return True
    except ValueError:
        return False


class AddAppDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Tk,
        config_data: dict,
        on_saved,
        app_data: dict | None = None,
        original_app_name: str | None = None,
        original_server_name: str | None = None,
        selected_server: str | None = None,
    ):
        super().__init__(parent)
        self.title("Add Application" if app_data is None else "Edit Application")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.on_saved = on_saved
        self.config_data = config_data
        self.app_data = app_data or {}
        self.original_app_name = original_app_name
        self.original_server_name = original_server_name or selected_server

        self.server_names = [s.get("name", "") for s in self.config_data.get("servers", [])]
        if not self.server_names:
            self.server_names = ["Default"]

        self.name_var = tk.StringVar(value=self.app_data.get("name", ""))
        self.server_var = tk.StringVar(value=selected_server or self.server_names[0])
        self.ip_var = tk.StringVar(value=self.app_data.get("ip", ""))
        self.port_var = tk.StringVar(value=str(self.app_data.get("port", "")))
        self.protocol_var = tk.StringVar(value=self.app_data.get("protocol", "http"))
        self.path_var = tk.StringVar(value=self.app_data.get("path", ""))
        self.enabled_var = tk.BooleanVar(value=bool(self.app_data.get("enabled", True)))

        self._build_ui()
        _center_window(self, 430, 360)
        self.transient(parent)
        self.grab_set()

    def _build_ui(self) -> None:
        def make_label(text: str) -> tk.Label:
            return tk.Label(self, text=text, bg=BG, fg=FG, font=FONT, anchor="w")

        def make_entry(var: tk.StringVar) -> tk.Entry:
            return tk.Entry(
                self,
                textvariable=var,
                bg="#2A2A3E",
                fg=FG,
                insertbackground=FG,
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground=BORDER,
                highlightcolor=BORDER,
                font=FONT,
            )

        make_label("Application name").grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
        make_entry(self.name_var).grid(row=1, column=0, sticky="ew", padx=(12, 6))

        make_label("Server").grid(row=0, column=1, sticky="w", padx=(6, 12), pady=(10, 2))
        server_menu = tk.OptionMenu(self, self.server_var, *self.server_names)
        server_menu.config(bg="#2A2A3E", fg=FG, activebackground=BORDER, activeforeground=FG, relief="solid", bd=1)
        server_menu["menu"].config(bg="#2A2A3E", fg=FG)
        server_menu.grid(row=1, column=1, sticky="ew", padx=(6, 12))

        make_label("IP / Hostname").grid(row=2, column=0, sticky="w", padx=12, pady=(10, 2))
        make_entry(self.ip_var).grid(row=3, column=0, columnspan=2, sticky="ew", padx=12)

        make_label("Port").grid(row=4, column=0, sticky="w", padx=12, pady=(10, 2))
        make_entry(self.port_var).grid(row=5, column=0, columnspan=2, sticky="ew", padx=12)

        make_label("Path suffix (optional)").grid(row=6, column=0, sticky="w", padx=12, pady=(10, 2))
        make_entry(self.path_var).grid(row=7, column=0, columnspan=2, sticky="ew", padx=12)

        protocol_frame = tk.Frame(self, bg=BG)
        protocol_frame.grid(row=8, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 0))
        tk.Label(protocol_frame, text="Protocol", bg=BG, fg=FG, font=FONT).pack(anchor="w")
        tk.Radiobutton(
            protocol_frame,
            text="http",
            variable=self.protocol_var,
            value="http",
            bg=BG,
            fg=FG,
            selectcolor="#2A2A3E",
            activebackground=BG,
            activeforeground=FG,
        ).pack(side="left", padx=(0, 8))
        tk.Radiobutton(
            protocol_frame,
            text="https",
            variable=self.protocol_var,
            value="https",
            bg=BG,
            fg=FG,
            selectcolor="#2A2A3E",
            activebackground=BG,
            activeforeground=FG,
        ).pack(side="left")
        tk.Radiobutton(
            protocol_frame,
            text="tcp",
            variable=self.protocol_var,
            value="tcp",
            bg=BG,
            fg=FG,
            selectcolor="#2A2A3E",
            activebackground=BG,
            activeforeground=FG,
        ).pack(side="left", padx=(8, 0))
        tk.Radiobutton(
            protocol_frame,
            text="udp",
            variable=self.protocol_var,
            value="udp",
            bg=BG,
            fg=FG,
            selectcolor="#2A2A3E",
            activebackground=BG,
            activeforeground=FG,
        ).pack(side="left", padx=(8, 0))

        tk.Checkbutton(
            self,
            text="Enabled",
            variable=self.enabled_var,
            bg=BG,
            fg=FG,
            selectcolor="#2A2A3E",
            activebackground=BG,
            activeforeground=FG,
        ).grid(row=9, column=0, sticky="w", padx=12, pady=(8, 4))

        button_frame = tk.Frame(self, bg=BG)
        button_frame.grid(row=10, column=0, columnspan=2, sticky="e", padx=12, pady=12)
        tk.Button(
            button_frame,
            text="Add Application" if not self.app_data else "Save",
            command=self._save,
            bg=ACCENT,
            fg="#11111B",
            relief="flat",
            padx=10,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(side="left", padx=6)
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            bg="#2A2A3E",
            fg=FG,
            relief="flat",
            padx=10,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(
            side="left"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _save(self) -> None:
        name = self.name_var.get().strip()
        server_name = self.server_var.get().strip()
        ip = self.ip_var.get().strip()
        port_raw = self.port_var.get().strip()
        protocol = self.protocol_var.get().strip()
        path = self.path_var.get().strip()

        if not name:
            messagebox.showerror("Validation", "Application name is required.")
            return
        if not _valid_host(ip):
            messagebox.showerror("Validation", "Enter a valid IPv4 address.")
            return
        try:
            port = int(port_raw)
            if port < 1 or port > 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation", "Port must be an integer between 1 and 65535.")
            return
        if protocol not in {"http", "https", "tcp", "udp"}:
            messagebox.showerror("Validation", "Protocol must be http, https, tcp, or udp.")
            return
        if protocol in {"http", "https"} and path and not path.startswith("/"):
            path = f"/{path}"

        app = {
            "name": name,
            "ip": ip,
            "port": port,
            "protocol": protocol,
            "path": path,
            "enabled": bool(self.enabled_var.get()),
        }

        if self.app_data and self.original_app_name and self.original_server_name:
            config_store.remove_application(self.original_server_name, self.original_app_name)
        config_store.add_application(server_name, app)
        config_store.save_config(config_store.load_config())

        if self.on_saved:
            self.on_saved()
        self.destroy()


def show_add_app_dialog(
    on_saved,
    app_data: dict | None = None,
    server_name: str | None = None,
    original_name: str | None = None,
    original_server_name: str | None = None,
) -> None:
    config_data = config_store.load_config()
    root = tk.Tk()
    root.withdraw()
    dialog = AddAppDialog(
        root,
        config_data,
        on_saved=on_saved,
        app_data=app_data,
        selected_server=server_name,
        original_app_name=original_name,
        original_server_name=original_server_name,
    )
    root.wait_window(dialog)
    root.destroy()

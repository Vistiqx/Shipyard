import sys
import tkinter as tk
from tkinter import messagebox

import winreg

import config as config_store
from ui.add_app_dialog import show_add_app_dialog


BG = "#1E1E2E"
FG = "#E8E8F8"
ACCENT = "#AC8FFE"
BORDER = "#4C3D75"
FONT = ("Segoe UI", 10)

STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "Shipyard"


def set_startup(enabled: bool):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE)
    if enabled:
        exe_path = sys.executable if getattr(sys, "frozen", False) else f'pythonw "{sys.argv[0]}"'
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)


def get_startup() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def _center_window(window: tk.Toplevel, width: int, height: int) -> None:
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, on_saved):
        super().__init__(parent)
        self.configure(bg=BG)
        self.title("Shipyard Settings")
        self.on_saved = on_saved
        self.config_data = config_store.load_config()

        self.launch_var = tk.BooleanVar(value=bool(self.config_data.get("settings", {}).get("launch_at_startup", get_startup())))
        self.interval_var = tk.IntVar(value=int(self.config_data.get("settings", {}).get("health_check_interval_seconds", 60)))
        self.timeout_var = tk.IntVar(value=int(self.config_data.get("settings", {}).get("health_check_timeout_seconds", 5)))

        self._build_ui()
        _center_window(self, 960, 700)
        self.transient(parent)
        self.grab_set()

    def _build_ui(self) -> None:
        title = tk.Label(self, text="Shipyard Settings", bg=BG, fg=FG, font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w", padx=12, pady=10)

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=12)

        server_frame = tk.LabelFrame(top, text="Servers", bg=BG, fg=FG, font=("Segoe UI", 10, "bold"))
        server_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.server_list_frame = tk.Frame(server_frame, bg=BG)
        self.server_list_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self._render_servers()

        add_server_frame = tk.Frame(server_frame, bg=BG)
        add_server_frame.pack(fill="x", padx=6, pady=6)
        self.new_server_name = tk.StringVar()
        
        tk.Entry(
            add_server_frame,
            textvariable=self.new_server_name,
            bg="#2A2A3E",
            fg=FG,
            insertbackground=FG,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(
            add_server_frame,
            text="+ Add server",
            command=self._add_server,
            bg=ACCENT,
            fg="#11111B",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(
            side="left"
        )

        settings_frame = tk.LabelFrame(top, text="Global Settings", bg=BG, fg=FG, font=("Segoe UI", 10, "bold"))
        settings_frame.pack(side="left", fill="y", padx=(6, 0))

        tk.Checkbutton(
            settings_frame,
            text="Launch at Windows startup",
            variable=self.launch_var,
            command=lambda: set_startup(bool(self.launch_var.get())),
            bg=BG,
            fg=FG,
            selectcolor="#2A2A3E",
            activebackground=BG,
            activeforeground=FG,
        ).pack(anchor="w", padx=8, pady=8)
        tk.Label(settings_frame, text="Health check interval (s)", bg=BG, fg=FG, font=FONT).pack(anchor="w", padx=8)
        tk.Spinbox(
            settings_frame,
            from_=10,
            to=3600,
            textvariable=self.interval_var,
            width=8,
            bg="#2A2A3E",
            fg=FG,
            buttonbackground="#2A2A3E",
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(anchor="w", padx=8, pady=(0, 8))
        tk.Label(settings_frame, text="Health check timeout (s)", bg=BG, fg=FG, font=FONT).pack(anchor="w", padx=8)
        tk.Spinbox(
            settings_frame,
            from_=1,
            to=30,
            textvariable=self.timeout_var,
            width=8,
            bg="#2A2A3E",
            fg=FG,
            buttonbackground="#2A2A3E",
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(anchor="w", padx=8, pady=(0, 8))

        apps_frame = tk.LabelFrame(self, text="Applications", bg=BG, fg=FG, font=("Segoe UI", 10, "bold"))
        apps_frame.pack(fill="both", expand=True, padx=12, pady=10)

        canvas = tk.Canvas(apps_frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(apps_frame, orient="vertical", command=canvas.yview)
        self.app_list_frame = tk.Frame(canvas, bg=BG)
        self.app_list_frame.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.app_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._render_apps()

        buttons = tk.Frame(self, bg=BG)
        buttons.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(
            buttons,
            text="Save",
            command=self._save,
            bg=ACCENT,
            fg="#11111B",
            relief="flat",
            padx=12,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(side="right", padx=6)
        tk.Button(
            buttons,
            text="Cancel",
            command=self.destroy,
            bg="#2A2A3E",
            fg=FG,
            relief="flat",
            padx=12,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            font=FONT,
        ).pack(side="right")

    def _render_servers(self) -> None:
        for child in self.server_list_frame.winfo_children():
            child.destroy()
        for server in self.config_data.get("servers", []):
            row = tk.Frame(self.server_list_frame, bg=BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{server.get('name')}", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(side="left", anchor="w")
            tk.Button(
                row,
                text="✕ Remove",
                command=lambda s=server.get("name"): self._remove_server(s),
                bg="#713E5A",
                fg=FG,
                relief="flat",
            ).pack(side="right")

    def _render_apps(self) -> None:
        for child in self.app_list_frame.winfo_children():
            child.destroy()
        for server in self.config_data.get("servers", []):
            tk.Label(
                self.app_list_frame,
                text=server.get("name", ""),
                bg=BG,
                fg=ACCENT,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(8, 2))
            for app in server.get("applications", []):
                row = tk.Frame(self.app_list_frame, bg=BG)
                row.pack(fill="x", pady=2)
                enabled_var = tk.BooleanVar(value=bool(app.get("enabled", True)))
                endpoint = app.get("url") or f"{app.get('ip')}:{app.get('port')}"
                tk.Checkbutton(
                    row,
                    variable=enabled_var,
                    command=lambda sv=server.get("name"), an=app.get("name"), v=enabled_var: self._toggle(sv, an, v.get()),
                    bg=BG,
                    activebackground=BG,
                    selectcolor="#2A2A3E",
                ).pack(side="left")
                tk.Label(
                    row,
                    text=(
                        f"{app.get('name')}  {endpoint}  "
                        f"{app.get('protocol')}  path={app.get('path', '')!s}"
                    ),
                    bg=BG,
                    fg=FG,
                ).pack(side="left")
                tk.Button(
                    row,
                    text="Edit",
                    command=lambda a=app.copy(), s=server.get("name"): self._edit_app(s, a),
                    bg="#355C7D",
                    fg=FG,
                    relief="flat",
                ).pack(side="right", padx=4)
                tk.Button(
                    row,
                    text="Remove",
                    command=lambda s=server.get("name"), a=app.get("name"): self._remove_app(s, a),
                    bg="#713E5A",
                    fg=FG,
                    relief="flat",
                ).pack(side="right")

    def _add_server(self) -> None:
        name = self.new_server_name.get().strip()
        if not name:
            messagebox.showerror("Validation", "Server name is required.")
            return
        self.config_data.setdefault("servers", []).append({"name": name, "applications": []})
        self.new_server_name.set("")
        self._render_servers()

    def _remove_server(self, server_name: str) -> None:
        if not messagebox.askyesno("Confirm", f"Remove server '{server_name}' and all applications?"):
            return
        self.config_data["servers"] = [s for s in self.config_data.get("servers", []) if s.get("name") != server_name]
        self._render_servers()
        self._render_apps()

    def _toggle(self, server_name: str, app_name: str, enabled: bool) -> None:
        for server in self.config_data.get("servers", []):
            if server.get("name") != server_name:
                continue
            for app in server.get("applications", []):
                if app.get("name") == app_name:
                    app["enabled"] = bool(enabled)

    def _remove_app(self, server_name: str, app_name: str) -> None:
        if not messagebox.askyesno("Confirm", f"Remove application '{app_name}'?"):
            return
        for server in self.config_data.get("servers", []):
            if server.get("name") == server_name:
                server["applications"] = [a for a in server.get("applications", []) if a.get("name") != app_name]
                break
        self._render_apps()

    def _edit_app(self, server_name: str, app: dict) -> None:
        self.withdraw()
        show_add_app_dialog(
            on_saved=None,
            app_data=app,
            server_name=server_name,
            original_name=app.get("name"),
            original_server_name=server_name,
        )
        self.config_data = config_store.load_config()
        self.deiconify()
        self._render_servers()
        self._render_apps()

    def _save(self) -> None:
        self.config_data.setdefault("settings", {})["launch_at_startup"] = bool(self.launch_var.get())
        self.config_data["settings"]["health_check_interval_seconds"] = int(self.interval_var.get())
        self.config_data["settings"]["health_check_timeout_seconds"] = int(self.timeout_var.get())
        config_store.save_config(self.config_data)
        set_startup(bool(self.launch_var.get()))
        if self.on_saved:
            self.on_saved()
        self.destroy()


def show_settings_dialog(on_saved) -> None:
    root = tk.Tk()
    root.withdraw()
    dialog = SettingsDialog(root, on_saved=on_saved)
    root.wait_window(dialog)
    root.destroy()

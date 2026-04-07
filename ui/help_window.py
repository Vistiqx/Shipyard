import tkinter as tk

from docs.help_content import HELP_TEXT


BG = "#1E1E2E"
FG = "#E8E8F8"
ACCENT = "#AC8FFE"


def _center_window(window: tk.Toplevel, width: int, height: int) -> None:
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class HelpWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Shipyard Help")
        self.configure(bg=BG)
        self._build_ui()
        _center_window(self, 700, 550)

    def _build_ui(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            frame,
            yscrollcommand=scrollbar.set,
            bg="#151522",
            fg=FG,
            wrap="word",
            padx=12,
            pady=10,
            relief="flat",
            insertbackground=FG,
        )
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        text.tag_configure("heading", font=("Segoe UI", 12, "bold"), foreground=ACCENT, spacing1=12, spacing3=4)
        text.tag_configure("body", font=("Segoe UI", 10), foreground=FG, spacing1=2, spacing3=6)

        for entry_type, content in HELP_TEXT:
            if entry_type == "heading":
                text.insert("end", f"{content}\n", "heading")
            else:
                text.insert("end", f"{content}\n", "body")

        text.config(state="disabled")


def show_help_window() -> None:
    root = tk.Tk()
    root.withdraw()
    window = HelpWindow(root)
    window.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

import customtkinter as ctk
from tkinter import filedialog
import webbrowser
from core.quote_builder import build_quote
from gui.preview_window import PreviewWindow
from gui.change_pricing_window import ChangePricingWindow
from gui.change_template_window import ChangeTemplateWindow


class MainWindow:

    def __init__(self, root):
        # v1.0
        self.root = root
        root.title("Quoter")
        root.geometry("900x600")

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # ---------- HEADER ----------
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(title_frame, text="Quoter", font=("Arial", 30, "bold"))
        title.pack(side="left")

        version = ctk.CTkLabel(title_frame, text="V1.0", font=("Arial", 14, "italic"))
        version.pack(side="left", padx=(8, 0), pady=(10, 0))

        self.settings_btn = ctk.CTkButton(
            header,
            text="⚙",
            width=40,
            height=40,
            corner_radius=8,
            command=self.open_settings
        )

        self.settings_btn.grid(row=0, column=1)

        # ---------- TEXT AREA ----------
        self.text = ctk.CTkTextbox(self.main_frame, font=("Arial", 16), height=350)
        self.text.pack(fill="both", expand=True, pady=10)

        # ---------- BUTTON ROW ----------
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        self.file_btn = ctk.CTkButton(
            btn_frame,
            text="Import File",
            command=self.import_file
        )
        self.file_btn.pack(side="left", padx=10)

        self.parse_btn = ctk.CTkButton(
            btn_frame,
            text="Parse",
            command=self.parse
        )
        self.parse_btn.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(
            btn_frame,
            text="Reset",
            command=self.reset
        )
        self.reset_btn.pack(side="right", padx=10)

    # ---------- FUNCTIONS ----------

    def import_file(self):

        path = filedialog.askopenfilename(
            title="Select booking message file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = f.read()

        self.text.delete("1.0", "end")
        self.text.insert("1.0", data)

    def parse(self):

        message = self.text.get("1.0", "end")

        try:
            result = build_quote(message)
            PreviewWindow(self.root, result)

        except Exception as e:
            print("Parse error:", e)

    def reset(self):

        self.text.delete("1.0", "end")

    def open_settings(self):

        win = ctk.CTkToplevel(self.root)
        win.title("Settings")
        win.geometry("300x300")

        ctk.CTkLabel(win, text="Settings", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkButton(
            win,
            text="Change Pricing",
            command=lambda: ChangePricingWindow(self.root)
        ).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(
            win,
            text="Change Template",
            command=lambda: ChangeTemplateWindow(self.root)
        ).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(win, text="How much we helped?").pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(win, text="Help", command=self.open_help).pack(fill="x", padx=20, pady=5)

        footer = ctk.CTkLabel(win, text="V1.0 | Get Data")
        footer.pack(side="bottom", pady=10)

    def open_help(self):
        webbrowser.open("https://google.com")

if __name__ == "__main__":

    root = ctk.CTk()
    MainWindow(root)
    root.mainloop()
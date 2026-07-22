import customtkinter as ctk
from tkinter import filedialog
import webbrowser

from core.quote_builder import build_quote

from gui.preview_window import PreviewWindow
from gui.change_pricing_window import ChangePricingWindow
from gui.change_template_window import ChangeTemplateWindow
from gui.settings_window import SettingsWindow
from PIL import Image, ImageTk

class MainWindow:

    def __init__(self, root):

        self.root = root
        self.windows = {}

        root.title("Quoter")
        root.geometry("900x600")

        self.icon = ImageTk.PhotoImage(
            Image.open("/home/sd/code/Quoter-main/assets/icon.png")         #TO-DO: Use a 256X256 actual pic not random pic
        )
        root.iconphoto(True, self.icon)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # ---------------- MAIN UI ----------------

        self.main_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0,10))

        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Quoter",
            font=("Arial",30,"bold")
        )
        title.grid(row=0,column=0,sticky="w")

        self.settings_btn = ctk.CTkButton(
            header,
            text="⚙",
            width=40,
            command=self.open_settings
        )
        self.settings_btn.grid(row=0,column=1)

        self.text = ctk.CTkTextbox(
            self.main_frame,
            height=350
        )
        self.text.pack(fill="both",expand=True,pady=10)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Import File",
            command=self.import_file
        ).pack(side="left",padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Parse",
            command=self.parse
        ).pack(side="left",padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Reset",
            command=self.reset
        ).pack(side="right",padx=5)

    # -------------------------------------------------------
    # Generic Window Manager
    # -------------------------------------------------------

    def open_window(self, key, window_class, *args, **kwargs):

        if key in self.windows:

            win = self.windows[key]

            if win.winfo_exists():
                win.lift()
                win.focus_force()
                return win

            del self.windows[key]

        win = window_class(*args, **kwargs)
        win.iconphoto(True, self.icon)
        self.windows[key] = win

        def close():

            self.windows.pop(key, None)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", close)

        return win

    # -------------------------------------------------------
    # Button callbacks
    # -------------------------------------------------------

    def open_settings(self):

        self.open_window(
            "settings",
            SettingsWindow,
            self.root,
            self
        )

    def parse(self):

        message = self.text.get("1.0","end")

        try:

            result = build_quote(message)

            self.open_window(
                "preview",
                PreviewWindow,
                self.root,
                result
            )

        except Exception as e:

            print(e)

    def import_file(self):

        path = filedialog.askopenfilename()

        if not path:
            return

        with open(path,"r",encoding="utf8") as f:
            self.text.delete("1.0","end")
            self.text.insert("1.0",f.read())

    def reset(self):

        self.text.delete("1.0","end")

    def open_help(self):

        webbrowser.open(
            "https://github.com/Ucoder69/Quoter/blob/main/README.md"
        )


if __name__ == "__main__":

    root = ctk.CTk()

    MainWindow(root)

    root.mainloop()
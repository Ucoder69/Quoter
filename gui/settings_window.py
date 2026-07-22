import customtkinter as ctk

from gui.change_pricing_window import ChangePricingWindow
from gui.change_template_window import ChangeTemplateWindow


class SettingsWindow(ctk.CTkToplevel):

    def __init__(self, root, main):

        super().__init__(root)

        self.main = main

        self.title("Settings")
        self.geometry("320x330")
        self.resizable(False, False)

        # ---------------- Title ----------------

        ctk.CTkLabel(
            self,
            text="Settings",
            font=("Arial", 20, "bold")
        ).pack(pady=(20, 15))

        # ---------------- Buttons ----------------

        ctk.CTkButton(
            self,
            text="Change Pricing",
            command=lambda: self.main.open_window(
                "pricing",
                ChangePricingWindow,
                self.master
            )
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            self,
            text="Change Template",
            command=lambda: self.main.open_window(
                "template",
                ChangeTemplateWindow,
                self.master
            )
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            self,
            text="How Much We Helped?"
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            self,
            text="Help",
            command=self.main.open_help
        ).pack(fill="x", padx=20, pady=5)

        # ---------------- Footer ----------------

        ctk.CTkLabel(
            self,
            text="Quoter v1.1",
            font=("Arial", 12)
        ).pack(side="bottom", pady=15)
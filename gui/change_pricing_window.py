import json
import os
import customtkinter as ctk

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.json")


class ChangePricingWindow(ctk.CTkToplevel):

    def __init__(self, root):

        super().__init__(root)

        self.title("Change Pricing")
        self.geometry("700x600")

        self.load_config()

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # -------- UNIT SELECTOR --------
        self.unit_var = ctk.StringVar()

        self.unit_dropdown = ctk.CTkOptionMenu(
            main,
            values=self.get_unit_keys(),
            variable=self.unit_var,
            command=self.load_unit
        )
        self.unit_dropdown.pack(fill="x", pady=10)

        # -------- SCROLLABLE EDIT AREA --------
        self.scroll = ctk.CTkScrollableFrame(main)
        self.scroll.pack(fill="both", expand=True)
        self.enable_mouse_scroll(self.scroll)

        self.entries = {}

        # -------- BUTTONS --------
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Add Room", command=self.add_room).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Remove Room", command=self.remove_room).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Save", command=self.save).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)

        # load first room
        first = self.get_unit_keys()[0]
        self.unit_var.set(first)
        self.load_unit(first)

    # ---------------- CONFIG ----------------
    
    def enable_mouse_scroll(self, widget):

        def _scroll(event):
            widget._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _scroll_linux_up(event):
            widget._parent_canvas.yview_scroll(-1, "units")

        def _scroll_linux_down(event):
            widget._parent_canvas.yview_scroll(1, "units")

        widget.bind_all("<MouseWheel>", _scroll)      # Windows / Mac
        widget.bind_all("<Button-4>", _scroll_linux_up)   # Linux scroll up
        widget.bind_all("<Button-5>", _scroll_linux_down) # Linux scroll down

    def load_config(self):

        with open(CONFIG_PATH, "r") as f:
            self.config = json.load(f)

    def save_config(self):

        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    # ---------------- UTIL ----------------

    def get_unit_keys(self):

        return sorted(self.config["units"].keys())

    def convert(self, value):

        v = value.strip()

        if v.lower() in ["true", "false"]:
            return v.lower() == "true"

        try:
            return int(v)
        except:
            pass

        return v

    # ---------------- LOAD UNIT ----------------

    def load_unit(self, unit_key):

        for w in self.scroll.winfo_children():
            w.destroy()

        self.entries.clear()

        unit = self.config["units"][unit_key]

        for key, value in unit.items():

            if key == "extra_mattress_price":
                continue

            ctk.CTkLabel(self.scroll, text=key).pack(anchor="w", pady=(8, 2))

            entry = ctk.CTkEntry(self.scroll)
            entry.pack(fill="x")

            entry.insert(0, str(value))

            self.entries[key] = entry

        # ---------- EXTRA MATTRESS SECTION ----------
        ctk.CTkLabel(
            self.scroll,
            text="Extra Mattress Pricing",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=15)

        for key, value in unit["extra_mattress_price"].items():

            ctk.CTkLabel(self.scroll, text=key).pack(anchor="w", pady=(6, 2))

            entry = ctk.CTkEntry(self.scroll)
            entry.pack(fill="x")

            entry.insert(0, str(value))

            self.entries[f"extra_{key}"] = entry

    # ---------------- ADD ROOM ----------------

    def add_room(self):

        units = self.config["units"]

        numbers = [int(k.replace("_", "")) for k in units.keys()]
        next_id = max(numbers) + 1 if numbers else 1

        new_key = f"{next_id:02d}_"

        units[new_key] = {
            "parser_key": f"room{next_id}",
            "show_name": f"Room {next_id}",
            "type": "room",
            "base_price": 3000,
            "default_adults": 2,
            "max_adults": 2,
            "max_children": 1,
            "gst_percent": 12,
            "allow_extra_mattress": True,
            "extra_mattress_price": {
                "child_under_5_free": True,
                "child_price_under_12": 500,
                "adult_price": 800
            }
        }

        self.refresh_dropdown(new_key)

    # ---------------- REMOVE ROOM ----------------

    def remove_room(self):

        key = self.unit_var.get()

        del self.config["units"][key]

        keys = self.get_unit_keys()

        if not keys:
            return

        self.refresh_dropdown(keys[0])

    # ---------------- REFRESH ----------------

    def refresh_dropdown(self, select_key):

        keys = self.get_unit_keys()

        self.unit_dropdown.configure(values=keys)

        self.unit_var.set(select_key)

        self.load_unit(select_key)

    # ---------------- SAVE ----------------

    def save(self):

        unit_key = self.unit_var.get()
        unit = self.config["units"][unit_key]

        for key, entry in self.entries.items():

            value = self.convert(entry.get())

            if key.startswith("extra_"):

                subkey = key.replace("extra_", "")
                unit["extra_mattress_price"][subkey] = value

            else:

                unit[key] = value

        self.save_config()
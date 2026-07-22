import json
import os
import customtkinter as ctk

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "data", "templates.json")


class ChangeTemplateWindow(ctk.CTkToplevel):

    def __init__(self, root):

        super().__init__(root)

        self.title("Change Template")
        self.geometry("750x600")

        self.load_templates()

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # -------- TEMPLATE SELECTOR --------
        self.template_var = ctk.StringVar()

        self.dropdown = ctk.CTkOptionMenu(
            main,
            values=self.get_keys(),
            variable=self.template_var,
            command=self.load_template
        )
        self.dropdown.pack(fill="x", pady=10)

        # -------- SCROLLABLE EDIT AREA --------
        self.scroll = ctk.CTkScrollableFrame(main)
        self.scroll.pack(fill="both", expand=True)

        self.enable_scroll(self.scroll)

        # -------- BUTTONS --------
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Add Template", command=self.add_template).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Remove Template", command=self.remove_template).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Save", command=self.save).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)

        first = self.get_keys()[0]
        self.template_var.set(first)
        self.load_template(first)

    # ---------------- LOAD / SAVE ----------------

    def load_templates(self):

        with open(TEMPLATE_PATH, "r") as f:
            self.templates = json.load(f)

    def save_templates(self):

        with open(TEMPLATE_PATH, "w") as f:
            json.dump(self.templates, f, indent=2)

    # ---------------- UTIL ----------------

    def get_keys(self):

        return list(self.templates.keys())

    # ---------------- LOAD TEMPLATE ----------------

    def load_template(self, key):

        for w in self.scroll.winfo_children():
            w.destroy()

        template = self.templates[key]

        # TEMPLATE NAME
        ctk.CTkLabel(self.scroll, text="Template Name").pack(anchor="w", pady=(8, 2))

        self.name_entry = ctk.CTkEntry(self.scroll)
        self.name_entry.pack(fill="x")

        self.name_entry.insert(0, key)

        # SUBJECT
        ctk.CTkLabel(self.scroll, text="Subject").pack(anchor="w", pady=(12, 2))

        self.subject_entry = ctk.CTkEntry(self.scroll)
        self.subject_entry.pack(fill="x")

        self.subject_entry.insert(0, template.get("subject", ""))

        # BODY (more space)
        ctk.CTkLabel(self.scroll, text="Body HTML").pack(anchor="w", pady=(12, 2))

        self.body_box = ctk.CTkTextbox(self.scroll, height=300)
        self.body_box.pack(fill="both", expand=True)

        self.body_box.insert("1.0", template.get("body_html", ""))

    # ---------------- ADD TEMPLATE ----------------

    def add_template(self):

        name = "new_template"
        i = 1

        while name in self.templates:
            name = f"new_template_{i}"
            i += 1

        self.templates[name] = {
            "subject": "",
            "body_html": ""
        }

        self.refresh_dropdown(name)

    # ---------------- REMOVE TEMPLATE ----------------

    def remove_template(self):

        key = self.template_var.get()

        del self.templates[key]

        keys = self.get_keys()

        if not keys:
            return

        self.refresh_dropdown(keys[0])

    # ---------------- REFRESH ----------------

    def refresh_dropdown(self, select_key):

        keys = self.get_keys()

        self.dropdown.configure(values=keys)

        self.template_var.set(select_key)

        self.load_template(select_key)

    # ---------------- SAVE ----------------

    def save(self):

        old_key = self.template_var.get()
        new_key = self.name_entry.get().strip()

        data = {
            "subject": self.subject_entry.get(),
            "body_html": self.body_box.get("1.0", "end").strip()
        }

        if new_key != old_key:
            del self.templates[old_key]

        self.templates[new_key] = data

        self.save_templates()

        self.refresh_dropdown(new_key)

    # ---------------- SCROLL ----------------

    def enable_scroll(self, widget):

        def _scroll(event):
            widget._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _scroll_up(event):
            widget._parent_canvas.yview_scroll(-1, "units")

        def _scroll_down(event):
            widget._parent_canvas.yview_scroll(1, "units")

        widget.bind_all("<MouseWheel>", _scroll)
        widget.bind_all("<Button-4>", _scroll_up)
        widget.bind_all("<Button-5>", _scroll_down)
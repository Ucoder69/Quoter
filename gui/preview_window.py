import customtkinter as ctk
import pyperclip

from core.config_manager import ConfigManager
from core.template_manager import load_templates
from core.mailer_web import copy_email_to_clipboard
from core.calculator import calculate_total
from core.email_generator import generate_email


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class PreviewWindow(ctk.CTkToplevel):
    def TFrame(parent):
        return ctk.CTkFrame(parent, fg_color="transparent")
    
    def __init__(self, parent, result):

        super().__init__(parent)

        self.title("Quote Preview")
        self.geometry("1000x900")
        self.minsize(950, 780)

        self.result = result
        self.parsed = result["parsed"]

        self.config_mgr = ConfigManager()
        self.units_config = self.config_mgr.get_all_units()
        self.last_room_used = self.parsed["units"][0]

        self.room_id_to_name = {
            uid: data["show_name"]
            for uid, data in self.units_config.items()
        }

        self.room_name_to_id = {
            v: k for k, v in self.room_id_to_name.items()
        }

        self.people = self._build_people()

        self._build_layout()

        self._recalculate()

    # --------------------------------------------------
    # PEOPLE INITIALIZATION
    # --------------------------------------------------

    def _build_people(self):

        people = []

        default_room = self.parsed["units"][0]

        for _ in range(self.parsed["adults"]):
            people.append({"type": "adult", "room": default_room})

        for age in self.parsed["children_ages"] or []:
            people.append({
                "type": "child",
                "age": age,
                "room": default_room
            })

        return people

    # --------------------------------------------------
    # UI LAYOUT
    # --------------------------------------------------

    def _build_layout(self):

        self.container = self.TFrame()
        self.container.pack(fill="both", expand=True, padx=15, pady=20)

        # TOP — booking info
        self._build_booking_section()

        # GUESTS
        self._build_guest_section()

        # PRICE PREVIEW
        self._build_price_section()

        # TEMPLATE
        self._build_template_section()

        # BUTTONS
        self._build_buttons()

    # --------------------------------------------------
    # BOOKING SECTION
    # --------------------------------------------------

    def _build_booking_section(self):

        frame = ctk.CTkFrame(self.container)
        frame.pack(fill="x", pady=8)

        full = f"{self.parsed.get('first_name','')} {self.parsed.get('surname','')}"

        ctk.CTkLabel(frame, text="Guest Name").grid(row=0, column=0, padx=10)

        self.full_name = ctk.CTkEntry(frame, width=220)
        self.full_name.insert(0, full)
        self.full_name.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(frame, text="Title").grid(row=1, column=0)

        self.title_var = ctk.StringVar(value="Mr")

        ctk.CTkRadioButton(frame, text="Mr", variable=self.title_var, value="Mr").grid(row=1, column=1)
        ctk.CTkRadioButton(frame, text="Mrs", variable=self.title_var, value="Mrs").grid(row=1, column=2)
        ctk.CTkRadioButton(frame, text="Ms", variable=self.title_var, value="Ms").grid(row=1, column=3)

        ctk.CTkLabel(frame, text="Surname").grid(row=2, column=0)

        self.surname = ctk.CTkEntry(frame, width=160)
        self.surname.insert(0, self.parsed.get("surname", ""))
        self.surname.configure(state="disabled")
        self.surname.grid(row=2, column=1)

        ctk.CTkLabel(frame, text="Check-in").grid(row=3, column=0)

        self.checkin = ctk.CTkEntry(frame, width=180)
        self.checkin.insert(0, self.parsed.get("check_in", ""))
        self.checkin.grid(row=3, column=1)

        ctk.CTkLabel(frame, text="Check-out").grid(row=4, column=0)

        self.checkout = ctk.CTkEntry(frame, width=180)
        self.checkout.insert(0, self.parsed.get("check_out", ""))
        self.checkout.grid(row=4, column=1)

    # --------------------------------------------------
    # GUEST EDITOR
    # --------------------------------------------------

    def _build_guest_section(self):

        
        guest_block = self.TFrame()
        guest_block.pack(fill="x", pady=10, padx=10)

        self.guest_scroll = ctk.CTkScrollableFrame(
            guest_block,
            height=120
        )
        self.guest_scroll.pack(fill="x", padx=10, pady=10)

        self.people_frame = self.guest_scroll

        self._draw_people()

        controls = self.TFrame()
        controls.pack(pady=8)

        ctk.CTkButton(
            controls,
            text="Add Adult",
            width=120,
            command=self._add_adult
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            controls,
            text="Add Child",
            width=120,
            command=self._add_child
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            controls,
            text="Remove Guest",
            width=120,
            command=self._remove_guest
        ).pack(side="left", padx=5)

    def _draw_people(self):

        for w in self.people_frame.winfo_children():
            w.destroy()

        for p in self.people:

            row = ctk.CTkFrame(self.people_frame)
            row.pack(fill="x", pady=3)

            label = p["type"].capitalize()

            if p["type"] == "child":
                label += f" ({p['age']})"

            ctk.CTkLabel(
                row,
                text=label,
                width=90,
                anchor="w"
            ).pack(side="left", padx=10)

            combo = ctk.CTkComboBox(
                row,
                values=list(self.room_id_to_name.values()),
                width=220
            )
            def room_changed(choice):
                self.last_room_used = self.room_name_to_id[choice]
            combo.configure(command=room_changed)
            combo.set(self.room_id_to_name[p["room"]])
            combo.pack(side="left")

            p["widget"] = combo

    # --------------------------------------------------
    # ROOM SUMMARY
    # --------------------------------------------------

    def _build_summary_section(self):

        self.summary_frame =self.TFrame()
        self.summary_frame.pack(fill="x", pady=10, expand=False)

    # --------------------------------------------------
    # PRICE TABLE
    # --------------------------------------------------

    def _build_price_section(self):
        
        price_block = self.TFrame()
        price_block.pack(fill="x", pady=10, padx=10)

        # header
        header = ctk.CTkFrame(price_block)
        header.pack(fill="x", padx=10)

        columns = ["Unit", "Room Price", "GST", "GST Amount", "Total"]

        for i, col in enumerate(columns):

            ctk.CTkLabel(
                header,
                text=col,
                width=150,
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=i, padx=5)

        # scrollable rows
        self.price_scroll = ctk.CTkScrollableFrame(
            price_block,
            height=150
        )

        self.price_scroll.pack(fill="x", padx=10, pady=8)

        self.price_rows = self.price_scroll

    # --------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------

    def _build_template_section(self):

        frame = self.TFrame()
        frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(frame, text="Template").pack(side="left", padx=10)

        templates = list(load_templates().keys())

        self.template = ctk.CTkComboBox(frame, values=templates)

        if templates:
            self.template.set(templates[0])

        self.template.pack(side="left")

    # --------------------------------------------------
    # BUTTONS
    # --------------------------------------------------

    def _build_buttons(self):

        frame = self.TFrame()
        frame.pack(pady=20)

        ctk.CTkButton(frame, text="Recalculate", command=self._recalculate).pack(side="left", padx=6)
        ctk.CTkButton(frame, text="Copy Email", command=self._copy_email).pack(side="left", padx=6)
        ctk.CTkButton(frame, text="Copy Subject", command=self._copy_subject).pack(side="left", padx=6)
        ctk.CTkButton(frame, text="Copy Email ID", command=self._copy_email_id).pack(side="left", padx=6)
        ctk.CTkButton(frame, text="Reset", command=self.destroy).pack(side="left", padx=6)

    # --------------------------------------------------
    # GUEST CONTROLS
    # --------------------------------------------------

    def _add_adult(self):

        room = self.last_room_used
        

        self.people.append({"type": "adult", "room": room})

        self._draw_people()

    def _add_child(self):

        popup = ctk.CTkToplevel(self)
        popup.title("Child Age")
        popup.geometry("220x120")

        ctk.CTkLabel(popup, text="Enter Age").pack(pady=10)

        age_entry = ctk.CTkEntry(popup)
        age_entry.pack()

        def confirm():

            try:
                age = int(age_entry.get())
            except:
                return

            room = self.last_room_used

            self.people.append({
                "type": "child",
                "age": age,
                "room": room
            })

            popup.destroy()

            self._draw_people()

        ctk.CTkButton(popup, text="Add", command=confirm).pack(pady=10)

    def _remove_guest(self):

        if self.people:
            self.people.pop()

        self._draw_people()

    # --------------------------------------------------
    # CALCULATION
    # --------------------------------------------------

    def _recalculate(self):

        name_parts = self.full_name.get().split()

        if name_parts:

            surname = name_parts[-1]

            self.surname.configure(state="normal")
            self.surname.delete(0, "end")
            self.surname.insert(0, surname)
            self.surname.configure(state="disabled")

        room_data = {}

        for p in self.people:

            p["room"] = self.room_name_to_id[p["widget"].get()]

            r = p["room"]

            if r not in room_data:
                room_data[r] = {"adults": 0, "children": []}

            if p["type"] == "adult":
                room_data[r]["adults"] += 1
            else:
                room_data[r]["children"].append(p["age"])

        results = []
        total = 0

        for r, pax in room_data.items():

            unit = self.units_config[r]

            res = calculate_total(
                unit_config=unit,
                adults=pax["adults"],
                children_ages=pax["children"]
            )

            total += res["total"]

            results.append({
                "display_name": unit["show_name"],
                "subtotal": res["subtotal"],
                "gst_percent": unit["gst_percent"],
                "gst_amount": res["gst_amount"],
                "total": res["total"]
            })

        # price preview
        for w in self.price_rows.winfo_children():
            w.destroy()

        row = 0

        for r in results:

            values = [
                r["display_name"],
                f"₹{r['subtotal']}",
                f"{r['gst_percent']}%",
                f"₹{r['gst_amount']}",
                f"₹{r['total']}"
            ]

            for col, val in enumerate(values):

                ctk.CTkLabel(
                    self.price_rows,
                    text=val,
                    width=150,
                    anchor="w"
                ).grid(row=row, column=col, padx=5, pady=3)

            row += 1


        ctk.CTkLabel(
            self.price_rows,
            text="Grand Total",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=row, column=0, pady=6)

        ctk.CTkLabel(
            self.price_rows,
            text=f"₹{total}",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=row, column=4)


        # email
        surname = f"{self.title_var.get()} {self.surname.get()}"

        self.result["email"] = generate_email(
            first_name=self.parsed.get("first_name", ""),
            template_name=self.template.get(),
            surname=surname,
            check_in=self.checkin.get(),
            check_out=self.checkout.get(),
            units_data=results
        )

    # --------------------------------------------------
    # CLIPBOARD
    # --------------------------------------------------
    
    def _copy_email(self):

        copy_email_to_clipboard(self.result["email"]["body_html"])

    def _copy_subject(self):

        pyperclip.copy(self.result["email"]["subject"])

    def _copy_email_id(self):

        pyperclip.copy(self.parsed.get("email", ""))

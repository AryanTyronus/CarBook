"""Browse and manage cars page — Luxury Edition."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from typing import Dict, Optional

import customtkinter as ctk

try:
    from PIL import Image
except ImportError:
    Image = None

from services.car_service import CarService
from services.booking_service import BookingService
from ui.pages.base_page import BasePage
from theme.colors import *
from theme.typography import font_heading_lg, font_label, font_body_secondary
from utils.auth import Session


class BrowseCarsPage(BasePage):
    """Car inventory management page."""

    def __init__(self, master, app, is_admin=False, **kwargs):
        super().__init__(master, app, **kwargs)
        self.cars = []
        self.image_refs = []
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="all")
        self.status_var = tk.StringVar(value="all")
        self.message_label = None
        self.is_admin = is_admin
        self._setup_ui()

    def _setup_ui(self):
        """Build the page layout."""
        # Row 0: header (fixed), Row 1: controls (fixed),
        # Row 2: cars scrollable (expands), Row 3: status label (fixed)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(PAGE_PAD_Y, 12))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Manage Cars" if self.is_admin else "Browse Cars",
            font=font_heading_lg(bold=True),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w")

        # Add button — only for admins
        if self.is_admin:
            add_button = ctk.CTkButton(
                header,
                text="+ Add Car",
                width=120,
                height=38,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color=BG_DARK,
                font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
                corner_radius=CARD_RADIUS,
                command=self._open_add_dialog
            )
            add_button.grid(row=0, column=1, sticky="e")

        # Controls bar
        controls = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        controls.grid(row=1, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(0, 12))
        controls.grid_columnconfigure(0, weight=1)

        search_entry = ctk.CTkEntry(
            controls,
            textvariable=self.search_var,
            height=38,
            fg_color=BG_LIGHT,
            border_color=BORDER,
            placeholder_text="Search by brand, model, plate, or color",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(16, 10), pady=14)
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_cars())

        category_menu = ctk.CTkOptionMenu(
            controls,
            values=list(CarService.CATEGORIES),
            variable=self.category_var,
            width=130,
            fg_color=BG_LIGHT,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
            command=lambda _value: self.refresh_cars()
        )
        category_menu.grid(row=0, column=1, padx=10, pady=14)

        status_menu = ctk.CTkOptionMenu(
            controls,
            values=list(CarService.STATUSES),
            variable=self.status_var,
            width=140,
            fg_color=BG_LIGHT,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
            command=lambda _value: self.refresh_cars()
        )
        status_menu.grid(row=0, column=2, padx=(10, 16), pady=14)

        # Scrollable car grid — fills remaining vertical space
        self.cars_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BG_LIGHT,
            scrollbar_button_hover_color=BORDER,
            width=1000
        )
        self.cars_frame.grid(row=2, column=0, sticky="nsew", padx=PAGE_PAD_X, pady=(0, 4))
        # The internal canvas column must expand so cards fill the full width
        self.cars_frame.grid_columnconfigure(0, weight=1)

        # Status label at the very bottom
        self.message_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        self.message_label.grid(row=3, column=0, sticky="w", padx=PAGE_PAD_X, pady=(2, 10))

    def refresh_cars(self):
        """Reload and render car cards."""
        self._set_message("Loading cars...", TEXT_MUTED)
        self.update_idletasks()
        self.cars = CarService.get_all(
            search=self.search_var.get().strip(),
            category=self.category_var.get(),
            status=self.status_var.get()
        )
        self._render_cars()
        count = len(self.cars)
        self._set_message(f"{count} car{'s' if count != 1 else ''} shown", TEXT_SECONDARY)

    def _render_cars(self):
        """Render cars in a responsive card grid."""
        for widget in self.cars_frame.winfo_children():
            widget.destroy()

        self.image_refs.clear()

        # Always reconfigure 3 equal columns so they span the full frame width
        for col in range(3):
            self.cars_frame.grid_columnconfigure(col, weight=1, uniform="cars")

        if not self.cars:
            empty = ctk.CTkLabel(
                self.cars_frame,
                text="No cars found. Add a car to start building your fleet.",
                font=ctk.CTkFont(size=15, family="Helvetica"),
                text_color=TEXT_MUTED
            )
            empty.grid(row=0, column=0, sticky="ew", pady=60, columnspan=3)
            return

        for index, car in enumerate(self.cars):
            row = index // 3
            column = index % 3
            self._create_car_card(car, row, column)

    def _create_car_card(self, car: Dict, row: int, column: int):
        """Create one car card — luxury styling with subtle border."""
        card = ctk.CTkFrame(
            self.cars_frame,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        card.grid(row=row, column=column, sticky="nsew", padx=8, pady=10)
        card.grid_columnconfigure(0, weight=1)

        def _open_details(selected=car):
            details_page = self.app.pages.get("car_details")
            if details_page:
                details_page.set_car(selected)
                self.app.show_page("car_details")

        # Clicking card body should open Car Details (no full-area overlay button)
        def _card_click(_event, selected=car):
            _open_details(selected)
            return "break"

        card.bind("<Button-1>", _card_click)

        image_widget = self._build_image_widget(card, car.get("image_url"))
        image_widget.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 12))

        name = ctk.CTkLabel(
            card,
            text=f"{car['brand']} {car['model']}",
            font=font_label(size=15, bold=True),
            text_color=TEXT_PRIMARY
        )
        name.grid(row=1, column=0, sticky="w", padx=18, pady=(8, 0))

        details = ctk.CTkLabel(
            card,
            text=f"{car['year']} • {car['category'].title()} • {car['seats']} seats",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        details.grid(row=2, column=0, sticky="w", padx=18, pady=(8, 0))

        plate = ctk.CTkLabel(
            card,
            text=f"{car['license_plate']} · ₹{car['daily_rate']:,.0f}/day",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=PRIMARY
        )
        plate.grid(row=3, column=0, sticky="w", padx=18, pady=(8, 0))

        # Premium status chip (subtle, modern)
        status_bg = self._status_bg(car["status"])
        status = ctk.CTkFrame(
            card,
            fg_color=status_bg,
            corner_radius=999,
            border_color=BORDER_LIGHT,
            border_width=1
        )
        status.grid(row=4, column=0, sticky="w", padx=18, pady=(12, 12))

        status_label = ctk.CTkLabel(
            status,
            text=car["status"].replace("_", " ").title(),
            font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
            text_color=self._status_color(car["status"])
        )
        status_label.pack(padx=14, pady=6)

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=5, column=0, sticky="ew", padx=16, pady=(4, 18))

        if not self.is_admin:
            actions.grid_propagate(False)
            actions.grid_rowconfigure(0, minsize=32)

            actions.grid_columnconfigure(0, weight=1)
            book_button = ctk.CTkButton(
                actions,
                text="Book",
                height=32,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color=BG_DARK,
                font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
                corner_radius=6,
                state="normal" if car["status"] in ("available", "rented") else "disabled",
                command=lambda selected=car: self._open_booking_dialog(selected)
            )
            book_button.grid(row=0, column=0, sticky="ew")

            # Prevent card click handler from also navigating when pressing the button
            book_button.bind("<Button-1>", lambda _e: "break")
        else:
            actions.grid_columnconfigure((0, 1, 2), weight=1)

            book_button = ctk.CTkButton(
                actions,
                text="Book",
                height=32,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color=BG_DARK,
                font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
                corner_radius=6,
                state="normal" if car["status"] in ("available", "rented") else "disabled",
                command=lambda selected=car: self._open_booking_dialog(selected)
            )
            book_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

            edit_button = ctk.CTkButton(
                actions,
                text="Edit",
                height=32,
                fg_color=BG_LIGHT,
                hover_color=BORDER,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(size=11, family="Helvetica"),
                corner_radius=6,
                command=lambda selected=car: self._open_edit_dialog(selected)
            )
            edit_button.grid(row=0, column=1, sticky="ew", padx=6)

            delete_button = ctk.CTkButton(
                actions,
                text="Delete",
                height=32,
                fg_color="transparent",
                hover_color=ACCENT_ERROR,
                text_color=ACCENT_ERROR,
                font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
                corner_radius=6,
                border_color=ACCENT_ERROR,
                border_width=1,
                command=lambda selected=car: self._delete_car(selected)
            )
            delete_button.grid(row=0, column=2, sticky="ew", padx=(6, 0))

            book_button.bind("<Button-1>", lambda _e: "break")
            edit_button.bind("<Button-1>", lambda _e: "break")
            delete_button.bind("<Button-1>", lambda _e: "break")

    def _build_image_widget(self, parent, image_path: Optional[str]):
        """Build an image preview or fallback placeholder."""
        if Image and image_path and Path(image_path).exists():
            image = ctk.CTkImage(
                light_image=Image.open(image_path),
                dark_image=Image.open(image_path),
                size=(240, 155)
            )
            self.image_refs.append(image)
            return ctk.CTkLabel(parent, text="", image=image, height=165)

        # Placeholder: fixed height maintained via grid_propagate(False)
        placeholder = ctk.CTkFrame(parent, fg_color=BG_LIGHT, corner_radius=8, height=165)
        placeholder.grid_propagate(False)
        placeholder.grid_columnconfigure(0, weight=1)
        placeholder.grid_rowconfigure(0, weight=1)

        icon = ctk.CTkLabel(
            placeholder,
            text="◆",
            font=ctk.CTkFont(size=28),
            text_color=BORDER_LIGHT
        )
        icon.grid(row=0, column=0)

        return placeholder

    def _open_add_dialog(self):
        self._open_car_dialog()

    def _open_edit_dialog(self, car: Dict):
        self._open_car_dialog(car)

    def _open_booking_dialog(self, car: Dict):
        """Open the booking form for a selected car — luxury styling."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Book Car")
        dialog.geometry("460x540")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_DARK)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        form = BookingForm(dialog, car)
        form.pack(fill="both", expand=True)
        form.on_cancel = dialog.destroy
        form.on_confirm = lambda values: self._create_booking(dialog, form, car, values)

    def _open_car_dialog(self, car: Optional[Dict] = None):
        """Open add/edit car dialog — luxury styling."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Car" if car else "Add Car")
        dialog.geometry("520x660")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_DARK)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        form = CarForm(dialog, car)
        form.pack(fill="both", expand=True)

        form.on_cancel = dialog.destroy
        form.on_save = lambda values: self._save_car(dialog, form, values, car)

    def _save_car(self, dialog, form, values: Dict, car: Optional[Dict]):
        if car:
            success, message = CarService.update(car["id"], values)
        else:
            success, message = CarService.create(values)

        if success:
            dialog.destroy()
            self._set_message(message, ACCENT_SUCCESS)
            self.refresh_cars()
        else:
            form.set_error(message)

    def _delete_car(self, car: Dict):
        ConfirmActionDialog(
            self,
            title="Delete Car?",
            message=f"{car['brand']} {car['model']} will be removed from the fleet.",
            confirm_text="Delete",
            confirm_color=ACCENT_ERROR,
            on_confirm=lambda: self._perform_delete_car(car)
        )

    def _perform_delete_car(self, car: Dict):
        self._set_message("Deleting car...", TEXT_MUTED)
        self.update_idletasks()
        success, message = CarService.delete(car["id"])
        self.refresh_cars()
        self._set_message(message, ACCENT_SUCCESS if success else ACCENT_ERROR)

    def _create_booking(self, dialog, form, car: Dict, values: Dict):
        success, message, booking = BookingService.create_booking(
            user_id=Session.get_user_id(),
            car_id=car["id"],
            start_date_text=values["start_date"],
            end_date_text=values["end_date"],
            pickup_location=values["pickup_location"],
            dropoff_location=values["dropoff_location"]
        )

        if not success:
            form.set_error(message)
            return

        dialog.destroy()
        self.refresh_cars()
        self._set_message(message, ACCENT_SUCCESS)
        BookingConfirmationDialog(self, booking)

    def _set_message(self, message: str, color: str):
        self.message_label.configure(text=message, text_color=color)

    @staticmethod
    def _status_color(status: str) -> str:
        return {
            "available": ACCENT_SUCCESS,
            "rented": PRIMARY,
            "maintenance": ACCENT_WARNING,
            "unavailable": ACCENT_ERROR,
        }.get(status, TEXT_SECONDARY)

    @staticmethod
    def _status_bg(status: str) -> str:
        return {
            "available": "#12301E",
            "rented": "#241F0A",
            "maintenance": "#2D2300",
            "unavailable": "#2A0D0D",
        }.get(status, BG_LIGHT)


class CarForm(ctk.CTkScrollableFrame):
    """Reusable add/edit form — luxury styling."""

    def __init__(self, master, car: Optional[Dict] = None):
        super().__init__(
            master,
            fg_color=BG_DARK,
            scrollbar_button_color=BG_LIGHT,
            scrollbar_button_hover_color=BORDER
        )
        self.car = car or {}
        self.on_save = None
        self.on_cancel = None
        self.entries = {}
        self.image_path = str(self.car.get("image_url") or "")
        self.error_label = None
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self,
            text="Edit Car" if self.car else "Add New Car",
            font=ctk.CTkFont(size=22, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w", padx=24, pady=(22, 16))

        fields = [
            ("brand", "Brand"),
            ("model", "Model"),
            ("year", "Year"),
            ("license_plate", "License Plate"),
            ("color", "Color"),
            ("daily_rate", "Daily Rate"),
            ("seats", "Seats"),
            ("description", "Description"),
        ]

        row = 1
        for key, label in fields:
            self._add_entry(row, key, label)
            row += 1

        self._add_option(row, "category", "Category", list(CarService.CATEGORIES[1:]))
        row += 1
        self._add_option(row, "status", "Availability", list(CarService.STATUSES[1:]))
        row += 1
        self._add_option(row, "transmission", "Transmission", list(CarService.TRANSMISSIONS))
        row += 1
        self._add_option(row, "fuel_type", "Fuel Type", list(CarService.FUEL_TYPES))
        row += 1

        image_button = ctk.CTkButton(
            self,
            text="Upload Image",
            height=36,
            fg_color=BG_LIGHT,
            hover_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            corner_radius=6,
            command=self._choose_image
        )
        image_button.grid(row=row, column=0, sticky="ew", padx=24, pady=(8, 4))
        row += 1

        self.image_label = ctk.CTkLabel(
            self,
            text=self._image_label_text(),
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_MUTED
        )
        self.image_label.grid(row=row, column=0, sticky="w", padx=24, pady=(0, 12))
        row += 1

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=ACCENT_ERROR
        )
        self.error_label.grid(row=row, column=0, sticky="w", padx=24, pady=(0, 10))
        row += 1

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=row, column=0, sticky="ew", padx=24, pady=(4, 22))
        actions.grid_columnconfigure((0, 1), weight=1)

        cancel = ctk.CTkButton(
            actions,
            text="Cancel",
            height=38,
            fg_color=BG_LIGHT,
            hover_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=lambda: self.on_cancel and self.on_cancel()
        )
        cancel.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        save = ctk.CTkButton(
            actions,
            text="Save Car",
            height=38,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self._save
        )
        save.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _add_entry(self, row: int, key: str, label: str):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", padx=24, pady=5)
        wrapper.grid_columnconfigure(0, weight=1)

        field_label = ctk.CTkLabel(
            wrapper,
            text=label,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        field_label.grid(row=0, column=0, sticky="w")

        value = "" if self.car.get(key) is None else str(self.car.get(key, ""))
        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            fg_color=BG_LIGHT,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            placeholder_text_color=TEXT_MUTED
        )
        entry.insert(0, value)
        entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.entries[key] = entry

    def _add_option(self, row: int, key: str, label: str, values):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", padx=24, pady=5)
        wrapper.grid_columnconfigure(0, weight=1)

        field_label = ctk.CTkLabel(
            wrapper,
            text=label,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        field_label.grid(row=0, column=0, sticky="w")

        selected = str(self.car.get(key) or values[0])
        variable = tk.StringVar(value=selected)
        menu = ctk.CTkOptionMenu(
            wrapper,
            values=values,
            variable=variable,
            height=36,
            fg_color=BG_LIGHT,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        menu.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.entries[key] = variable

    def _choose_image(self):
        selected = filedialog.askopenfilename(
            title="Choose car image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("All files", "*.*"),
            ]
        )
        copied = CarService.copy_image(selected)
        if copied:
            self.image_path = copied
            self.image_label.configure(text=self._image_label_text())

    def _save(self):
        values = {}
        for key, widget in self.entries.items():
            if isinstance(widget, tk.StringVar):
                values[key] = widget.get()
            else:
                values[key] = widget.get()

        values["image_url"] = self.image_path

        if self.on_save:
            self.on_save(values)

    def set_error(self, message: str):
        self.error_label.configure(text=message)

    def _image_label_text(self) -> str:
        if not self.image_path:
            return "No image selected"
        return Path(self.image_path).name


class BookingForm(ctk.CTkFrame):
    """Form for booking a selected car — luxury styling."""

    def __init__(self, master, car: Dict):
        super().__init__(master, fg_color=BG_DARK)
        self.car = car
        self.on_confirm = None
        self.on_cancel = None
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.pickup_var = tk.StringVar(value="Main Branch")
        self.dropoff_var = tk.StringVar(value="Main Branch")
        self.total_label = None
        self.error_label = None
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self,
            text=f"Book {self.car['brand']} {self.car['model']}",
            font=ctk.CTkFont(size=22, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 6))

        subtitle = ctk.CTkLabel(
            self,
            text=f"₹{self.car['daily_rate']:,.0f}/day · {self.car['license_plate']}",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=PRIMARY
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))

        self._add_entry(2, "Start Date", self.start_var, "YYYY-MM-DD")
        self._add_entry(3, "End Date", self.end_var, "YYYY-MM-DD")
        self._add_entry(4, "Pickup Location", self.pickup_var, "Main Branch")
        self._add_entry(5, "Dropoff Location", self.dropoff_var, "Main Branch")

        self.start_var.trace_add("write", lambda *_args: self._refresh_total())
        self.end_var.trace_add("write", lambda *_args: self._refresh_total())

        self.total_label = ctk.CTkLabel(
            self,
            text="Enter dates to calculate total",
            font=ctk.CTkFont(size=15, weight="bold", family="Helvetica"),
            text_color=PRIMARY
        )
        self.total_label.grid(row=6, column=0, sticky="w", padx=24, pady=(14, 8))

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=ACCENT_ERROR
        )
        self.error_label.grid(row=7, column=0, sticky="w", padx=24, pady=(0, 12))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=8, column=0, sticky="ew", padx=24, pady=(8, 24))
        actions.grid_columnconfigure((0, 1), weight=1)

        cancel = ctk.CTkButton(
            actions,
            text="Cancel",
            height=38,
            fg_color=BG_LIGHT,
            hover_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=lambda: self.on_cancel and self.on_cancel()
        )
        cancel.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        confirm = ctk.CTkButton(
            actions,
            text="Confirm Booking",
            height=38,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self._confirm
        )
        confirm.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _add_entry(self, row: int, label: str, variable: tk.StringVar, placeholder: str):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", padx=24, pady=6)
        wrapper.grid_columnconfigure(0, weight=1)

        field_label = ctk.CTkLabel(
            wrapper,
            text=label,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        field_label.grid(row=0, column=0, sticky="w")

        entry = ctk.CTkEntry(
            wrapper,
            textvariable=variable,
            height=38,
            fg_color=BG_LIGHT,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            placeholder_text=placeholder,
            placeholder_text_color=TEXT_MUTED
        )
        entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def _refresh_total(self):
        success, message, quote = BookingService.calculate_total(
            self.car["id"],
            self.start_var.get(),
            self.end_var.get()
        )
        if success:
            self.total_label.configure(
                text=f"{quote['total_days']} day(s) · Total ₹{quote['total_price']:,.0f}",
                text_color=PRIMARY
            )
            self.error_label.configure(text="")
        elif self.start_var.get() or self.end_var.get():
            self.total_label.configure(text="Enter valid dates to calculate total", text_color=TEXT_MUTED)
            self.error_label.configure(text=message)
        else:
            self.total_label.configure(text="Enter dates to calculate total", text_color=PRIMARY)
            self.error_label.configure(text="")

    def _confirm(self):
        if self.on_confirm:
            self.on_confirm({
                "start_date": self.start_var.get(),
                "end_date": self.end_var.get(),
                "pickup_location": self.pickup_var.get(),
                "dropoff_location": self.dropoff_var.get(),
            })

    def set_error(self, message: str):
        self.error_label.configure(text=message)


class BookingConfirmationDialog(ctk.CTkToplevel):
    """Confirmation dialog shown after a successful booking — luxury styling."""

    def __init__(self, master, booking: Dict):
        super().__init__(master)
        self.title("Booking Confirmed")
        self.geometry("440x420")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self._setup_ui(booking)

    def _setup_ui(self, booking: Dict):
        self.grid_columnconfigure(0, weight=1)

        # Elegant icon
        icon_label = ctk.CTkLabel(
            self,
            text="◆",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=PRIMARY
        )
        icon_label.grid(row=0, column=0, pady=(28, 8))

        title = ctk.CTkLabel(
            self,
            text="Booking Confirmed",
            font=ctk.CTkFont(size=22, weight="bold", family="Helvetica"),
            text_color=ACCENT_SUCCESS
        )
        title.grid(row=1, column=0, sticky="w", padx=28, pady=(0, 16))

        # Details card with subtle border
        details_card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        details_card.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 20))
        details_card.grid_columnconfigure(0, weight=1)

        details = [
            (f"{booking['brand']} {booking['model']}", TEXT_PRIMARY, True),
            (f"{booking['license_plate']}", TEXT_SECONDARY, False),
            (f"{booking['pickup_date'].date()} — {booking['dropoff_date'].date()}", TEXT_SECONDARY, False),
            (f"{booking['total_days']} day(s)", TEXT_SECONDARY, False),
            (f"₹{booking['total_price']:,.0f}", PRIMARY, True),
        ]

        for index, (text, color, bold) in enumerate(details):
            font = ctk.CTkFont(size=14, weight="bold" if bold else "normal", family="Helvetica")
            label = ctk.CTkLabel(
                details_card,
                text=text,
                font=font,
                text_color=color
            )
            label.grid(row=index, column=0, sticky="w", padx=20, pady=(8 if index > 0 else 14, 4))

        close = ctk.CTkButton(
            self,
            text="Done",
            height=42,
            width=160,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=13, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self.destroy
        )
        close.grid(row=3, column=0, pady=(0, 24))


class ConfirmActionDialog(ctk.CTkToplevel):
    """Reusable confirmation dialog for destructive actions — luxury styling."""

    def __init__(self, master, title: str, message: str, confirm_text: str, confirm_color: str, on_confirm):
        super().__init__(master)
        self.on_confirm = on_confirm
        self.title(title)
        self.geometry("440x260")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=21, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w", padx=28, pady=(28, 8))

        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14, family="Helvetica"),
            text_color=TEXT_SECONDARY,
            wraplength=380,
            justify="left"
        )
        message_label.grid(row=1, column=0, sticky="w", padx=28, pady=(0, 24))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=28, pady=(12, 28))
        actions.grid_columnconfigure((0, 1), weight=1)

        cancel = ctk.CTkButton(
            actions,
            text="Cancel",
            height=40,
            fg_color=BG_LIGHT,
            hover_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self.destroy
        )
        cancel.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        confirm = ctk.CTkButton(
            actions,
            text=confirm_text,
            height=40,
            fg_color=confirm_color,
            hover_color="#C62828" if confirm_color == ACCENT_ERROR else confirm_color,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self._confirm
        )
        confirm.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def _confirm(self):
        self.destroy()
        self.on_confirm()

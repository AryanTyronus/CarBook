"""Car add/edit form — luxury styling."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Dict, Optional

import customtkinter as ctk

from services.car_service import CarService
from theme.colors import ACCENT_ERROR, BG_DARK, BG_LIGHT, BORDER, CARD_RADIUS, PRIMARY, PRIMARY_HOVER, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY


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

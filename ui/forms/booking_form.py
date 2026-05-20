"""Booking form for car reservations — luxury styling."""

import tkinter as tk
from typing import Dict

import customtkinter as ctk

from services.booking_service import BookingService
from theme.colors import ACCENT_ERROR, BG_DARK, BG_LIGHT, BORDER, CARD_RADIUS, PRIMARY, PRIMARY_HOVER, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY


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

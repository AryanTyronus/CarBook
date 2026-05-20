"""Booking confirmation dialog shown after a successful booking — luxury styling."""

from typing import Dict
import customtkinter as ctk

from theme.colors import BG_CARD, BG_DARK, PRIMARY, PRIMARY_HOVER, ACCENT_SUCCESS, CARD_RADIUS, BORDER, TEXT_PRIMARY, TEXT_SECONDARY


class BookingConfirmationDialog(ctk.CTkToplevel):
    """Confirmation dialog shown after a successful booking."""

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

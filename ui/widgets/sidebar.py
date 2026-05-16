"""Sidebar navigation widget."""

import customtkinter as ctk
from typing import Callable, Dict, List

from theme.colors import *


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation component."""

    def __init__(
        self,
        master,
        items: List[Dict[str, str]],
        on_select: Callable[[str], None],
        **kwargs
    ):
        # Default styling
        kwargs.setdefault("fg_color", SIDEBAR_BG)
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("width", 240)

        super().__init__(master, **kwargs)

        self.items = items
        self.on_select = on_select
        self.buttons: Dict[str, ctk.CTkButton] = {}
        self.active_item = None
        # More elegant, refined icons
        self.icons = {
            "dashboard": "◇",
            "browse_cars": "◈",
            "my_bookings": "◷",
            "profile": "◉",
            "logout": "↗",
        }

        # Prevent the sidebar from resizing to fit its children.
        self.pack_propagate(False)

        # Explicitly set the fixed width.
        self.configure(width=240)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the sidebar UI components."""
        # Title/Logo area with subtle gold accent
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", pady=(24, 16), padx=20)

        title_label = ctk.CTkLabel(
            brand_frame,
            text="LUXURYDRIVE",
            font=ctk.CTkFont(size=18, weight="bold", family="Helvetica"),
            text_color=PRIMARY  # Gold accent
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            brand_frame,
            text="Premium Collection",
            font=ctk.CTkFont(size=11, family="Helvetica"),
            text_color=TEXT_MUTED
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Ultra-subtle separator
        separator = ctk.CTkFrame(self, fg_color=BORDER, height=1)
        separator.pack(fill="x", padx=16, pady=(0, 16))

        # Navigation items
        for item in self.items:
            self._create_nav_button(item)

    def _create_nav_button(self, item: Dict[str, str]):
        """Create a navigation button."""
        btn = ctk.CTkButton(
            self,
            text=f"  {self.icons.get(item['id'], '•')}  {item['label']}",
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color=SIDEBAR_HOVER,
            anchor="w",
            height=46,
            corner_radius=6,
            font=ctk.CTkFont(size=13, family="Helvetica"),
            command=lambda: self._on_item_click(item)
        )
        pady = (24, 2) if item["id"] == "logout" else 2
        btn.pack(fill="x", padx=12, pady=pady)

        self.buttons[item["id"]] = btn

    def _on_item_click(self, item: Dict[str, str]):
        """Handle item click."""
        if self.active_item:
            self.buttons[self.active_item].configure(
                fg_color="transparent",
                text_color=TEXT_SECONDARY
            )

        self.active_item = item["id"]
        self.buttons[item["id"]].configure(
            fg_color=SIDEBAR_ACTIVE,
            text_color=SIDEBAR_ACTIVE_TEXT  # Dark text on gold
        )

        if self.on_select:
            self.on_select(item["id"])

    def set_active(self, item_id: str):
        """Programmatically set active item."""
        if item_id in self.buttons:
            if self.active_item:
                self.buttons[self.active_item].configure(
                    fg_color="transparent",
                    text_color=TEXT_SECONDARY
                )
            self.active_item = item_id
            self.buttons[item_id].configure(
                fg_color=SIDEBAR_ACTIVE,
                text_color=SIDEBAR_ACTIVE_TEXT
            )
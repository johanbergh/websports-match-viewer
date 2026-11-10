import customtkinter as ctk

from src.config import *
from src.utils import shorten
from src.widgets import DataTable, LiveCard, TeamPanel, ghost_button

LOGO_DISPLAY_SIZE = 72

# (column id, heading, width, anchor, stretch)
BATTING_COLUMNS = [
    ("position", "#", 40, "center", False),
    ("name", "Batsman", 200, "w", True),
    ("runs", "R", 52, "center", False),
    ("balls", "B", 52, "center", False),
    ("fours", "4s", 44, "center", False),
    ("sixes", "6s", 44, "center", False),
    ("strike_rate", "SR", 64, "center", False),
    ("how_out", "How out", 190, "w", True),
]

BOWLING_COLUMNS = [
    ("name", "Bowler", 170, "w", True),
    ("overs", "O", 56, "center", False),
    ("runs", "R", 52, "center", False),
    ("wickets", "W", 44, "center", False),
    ("economy", "Econ", 64, "center", False),
]


class LandingScreen(ctk.CTkFrame):
    def __init__(self, master, on_submit):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self._on_submit = on_submit

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.place(relx=0.5, rely=0.42, anchor="center")

        ctk.CTkLabel(content, text="Websports Match Viewer", font=make_font(32, "bold"), text_color=ACCENT).pack(pady=(0, 40))

        self.url_entry = ctk.CTkEntry(content, width=380, height=54, corner_radius=18, border_width=3, border_color=ACCENT, fg_color="transparent", text_color=ACCENT,
            placeholder_text="Enter URL here...", placeholder_text_color=ACCENT_DIM,
            justify="center", font=make_font(16, "bold"),
        )
        self.url_entry.pack(pady=(0, 18))
        self.url_entry.bind("<Return>", lambda _event: self._submit())

        self.view_button = ctk.CTkButton(
            content, text="View Livegame", width=380, height=54, corner_radius=27,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=BTN_TEXT,
            text_color_disabled=BTN_TEXT, font=make_font(17, "bold"),
            command=self._submit,
        )
        self.view_button.pack()

        self.error_label = ctk.CTkLabel(content, text="", font=make_font(13), text_color=DANGER, wraplength=380)
        self.error_label.pack(pady=(16, 0))

        ctk.CTkLabel(self, text="Paste any link or game ID from websports.co.za", font=make_font(12), text_color=MUTED).place(relx=0.5, rely=0.95, anchor="center")
        ctk.CTkLabel(self, text="Copyright (C) 2026 Johan", font=make_font(12), text_color=MUTED).place(relx=0.5, rely=0.98, anchor="center")

    def _submit(self):
        self.error_label.configure(text="")
        self._on_submit(self.url_entry.get())

    def set_loading(self, is_loading):
        if is_loading:
            self.view_button.configure(text="Loading...", state="disabled")
        else:
            self.view_button.configure(text="View Livegame", state="normal")

    def show_error(self, message):
        self.error_label.configure(text=message)

    def clear_error(self):
        self.error_label.configure(text="")


class MatchScreen(ctk.CTkFrame):
    def __init__(self, master, on_back, on_toggle_pause, on_innings):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self._logo_cache = {}
        self._on_innings = on_innings

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # the scorecards take the spare space

        self._build_top_bar(on_back, on_toggle_pause)
        self._build_summary_card()
        self._build_live_strip()
        self._build_innings_selector()
        self._build_scorecards()
        self._build_status_bar()

    def _build_top_bar(self, on_back, on_toggle_pause):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 10))

        ghost_button(top_bar, "Back", on_back, width=90).pack(side="left")
        ctk.CTkLabel(top_bar, text="Websports Match Viewer", font=make_font(16, "bold"), text_color=ACCENT).pack(side="left", padx=18)

        # right-hand side is packed right to left
        self.pause_button = ghost_button(top_bar, "Pause", on_toggle_pause, width=96)
        self.pause_button.pack(side="right")

    def _build_summary_card(self):
        summary_card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20)
        summary_card.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        for column in range(3):
            summary_card.grid_columnconfigure(column, weight=1, uniform="summary")

        self.team_a_panel = TeamPanel(summary_card)
        self.team_a_panel.grid(row=0, column=0, padx=16, pady=18)

        match_info = ctk.CTkFrame(summary_card, fg_color="transparent")
        match_info.grid(row=0, column=1, padx=8, pady=18)

        self.match_title_label = ctk.CTkLabel(match_info, text="", font=make_font(13), text_color=MUTED, wraplength=300, justify="center")
        self.match_title_label.pack(pady=(8, 6))

        self.match_status_label = ctk.CTkLabel(match_info, text="", font=make_font(18, "bold"), text_color=ACCENT, wraplength=300, justify="center")
        self.match_status_label.pack()

        self.team_b_panel = TeamPanel(summary_card)
        self.team_b_panel.grid(row=0, column=2, padx=16, pady=18)

    def _build_live_strip(self):
        live_strip = ctk.CTkFrame(self, fg_color="transparent")
        live_strip.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        live_strip.grid_columnconfigure((0, 1), weight=1, uniform="strip")

        self.crease_card = LiveCard(live_strip, "AT THE CREASE")
        self.crease_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.bowling_card = LiveCard(live_strip, "BOWLING")
        self.bowling_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def _build_innings_selector(self):
        selector = ctk.CTkFrame(self, fg_color="transparent")
        selector.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 10))

        self.innings_buttons = []
        for innings_number in (1, 2):
            button = ctk.CTkButton(
                selector, text=f"Innings {innings_number}", width=190, height=38,
                corner_radius=19, font=make_font(13, "bold"), border_width=2,
                command=lambda number=innings_number: self._on_innings(number),
            )
            button.pack(side="left", padx=(0, 10))
            self.innings_buttons.append(button)

        self._highlight_innings_button(1)

    def _build_scorecards(self):
        scorecards = ctk.CTkFrame(self, fg_color="transparent")
        scorecards.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 12))
        scorecards.grid_rowconfigure(0, weight=1)
        scorecards.grid_columnconfigure(0, weight=3, uniform="scorecards")
        scorecards.grid_columnconfigure(1, weight=2, uniform="scorecards")

        self.batting_table = DataTable(scorecards, "Batting", BATTING_COLUMNS, has_footer=True, empty_text="No batting data yet")
        self.batting_table.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.bowling_table = DataTable(scorecards, "Bowling", BOWLING_COLUMNS, empty_text="No bowling data yet")
        self.bowling_table.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def _build_status_bar(self):
        status_bar = ctk.CTkFrame(self, fg_color=STATUS_BAR, corner_radius=0, height=34)
        status_bar.grid(row=5, column=0, sticky="ew")
        status_bar.grid_columnconfigure(0, weight=1)

        self.status_bar_label = ctk.CTkLabel(status_bar, text="Ready", font=make_font(12), text_color=MUTED)
        self.status_bar_label.grid(row=0, column=0, sticky="w", padx=24, pady=6)

        self.game_id_label = ctk.CTkLabel(status_bar, text="", font=make_font(12), text_color=MUTED)
        self.game_id_label.grid(row=0, column=1, sticky="e", padx=24, pady=6)

    def _get_logo_image(self, logo):
        """Turns a (name, PIL image) pair into a CTkImage, creating it only once."""
        logo_name, pil_image = logo
        if pil_image is None:
            return None

        if logo_name not in self._logo_cache:
            width, height = pil_image.size
            scale = LOGO_DISPLAY_SIZE / max(width, height)
            display_size = (max(1, int(width * scale)), max(1, int(height * scale)))
            self._logo_cache[logo_name] = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=display_size)
        return self._logo_cache[logo_name]

    def _highlight_innings_button(self, active_innings):
        for innings_number, button in enumerate(self.innings_buttons, start=1):
            if innings_number == active_innings:
                button.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER, border_color=ACCENT, text_color=BTN_TEXT)
            else:
                button.configure(fg_color="transparent", hover_color=CARD_ALT, border_color=CARD_ALT, text_color=TEXT)

    def reset(self, game_id):
        """Clears the screen so the previous match doesn't flash up."""
        self.match_title_label.configure(text="")
        self.match_status_label.configure(text="Loading…")
        self.team_a_panel.show_team("-", "-", "", None)
        self.team_b_panel.show_team("-", "-", "", None)
        self.crease_card.set_lines([])
        self.bowling_card.set_lines([])
        self.batting_table.clear()
        self.bowling_table.clear()
        self.batting_table.footer_label.configure(text="")
        for innings_number, button in enumerate(self.innings_buttons, start=1):
            button.configure(text=f"Innings {innings_number}")
        self._highlight_innings_button(1)
        self.game_id_label.configure(text=f"Game ID  {game_id}")
        self.set_message("Connecting…")

    def set_paused(self, is_paused):
        self.pause_button.configure(text="Resume" if is_paused else "Pause")
        if is_paused:
            self.set_message("Updates paused")

    def set_message(self, text, is_error=False):
        self.status_bar_label.configure(text=text, text_color=DANGER if is_error else MUTED)

    def set_active_innings(self, innings_number):
        self._highlight_innings_button(innings_number)

    def show_snapshot(self, snapshot, viewed_innings):
        self.team_a_panel.show_team(snapshot["team_a"], *snapshot["score_a"], self._get_logo_image(snapshot["logo_a"]))
        self.team_b_panel.show_team(snapshot["team_b"], *snapshot["score_b"], self._get_logo_image(snapshot["logo_b"]))

        self.match_title_label.configure(text=snapshot["title"])
        self.match_status_label.configure(text=snapshot["status"])

        # the innings buttons are named after the team that batted in each innings
        first_innings_name = snapshot["team_a"]
        second_innings_name = snapshot["team_b"]
        if first_innings_name == second_innings_name:
            first_innings_name += " (1st)"
            second_innings_name += " (2nd)"
        self.innings_buttons[0].configure(text=shorten(first_innings_name))
        self.innings_buttons[1].configure(text=shorten(second_innings_name))
        self._highlight_innings_button(viewed_innings)

        self.crease_card.set_lines(snapshot["crease"])
        self.bowling_card.set_lines(snapshot["bowlers"])
        self.batting_table.set_rows(snapshot["batting_rows"])
        self.batting_table.footer_label.configure(text=snapshot["extras"])
        self.bowling_table.set_rows(snapshot["bowling_rows"])
        self.set_message(f"Last update  {snapshot['updated']}")
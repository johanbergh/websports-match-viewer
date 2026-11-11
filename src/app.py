import queue
import threading
from tkinter import ttk

import customtkinter as ctk

from api import extract_game_id
from src.config import *
from src.screens import LandingScreen, MatchScreen
from src.presenter import build_snapshot

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title("Websports Match Viewer")
        self.geometry("1180x800")
        self.minsize(1000, 700)
        self._setup_table_style()

        # worker threads put finished results here, the UI thread picks them up
        self._ui_queue = queue.Queue()

        self.game_id = None
        self.innings_selected = 1
        self.innings_auto_selected = False
        self.paused = False

        # bumped every time a game is opened or closed, so results from an
        # old game can be recognised and thrown away
        self.session_id = 0
        self.fetching_session = None # session that currently has a request running
        self._poll_job = None
        self._queue_job = None

        self.landing_screen = LandingScreen(self, on_submit=self.open_game)
        self.match_screen = MatchScreen(self, on_back=self.show_landing, on_toggle_pause=self.toggle_pause, on_innings=self.select_innings)
        self._show_screen(self.landing_screen)

        self._process_ui_queue()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_table_style(self):
        """The scorecard tables are ttk Treeviews, so they need a ttk style."""
        try:
            window_scaling = self._get_window_scaling()
        except Exception:
            window_scaling = 1.0

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Match.Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT, rowheight=int(34 * window_scaling), borderwidth=0, relief="flat", font=(FONT_FAMILY, 11))
        style.configure("Match.Treeview.Heading", background=CARD_ALT, foreground=ACCENT, relief="flat", borderwidth=0, padding=(8, 7), font=(FONT_FAMILY, 10, "bold"))
        style.map("Match.Treeview", background=[("selected", CARD)], foreground=[("selected", TEXT)])
        style.map("Match.Treeview.Heading", background=[("active", CARD_ALT)])
        style.layout("Match.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    def _show_screen(self, screen):
        for other_screen in (self.landing_screen, self.match_screen):
            other_screen.pack_forget()
        screen.pack(fill="both", expand=True)

    def show_landing(self):
        self.session_id += 1
        self.fetching_session = None
        self._cancel_poll()
        self.paused = False
        self.match_screen.set_paused(False)
        self.landing_screen.set_loading(False)
        self.landing_screen.clear_error()
        self._show_screen(self.landing_screen)

    def open_game(self, user_input):
        game_id = extract_game_id(user_input)
        if not game_id:
            self.landing_screen.show_error("That isn't a Websports link or game ID.")
            return

        self.session_id += 1
        self._cancel_poll()
        self.game_id = game_id
        self.innings_selected = 1
        self.innings_auto_selected = False
        self.paused = False
        self.match_screen.set_paused(False)
        self.landing_screen.clear_error()
        self.landing_screen.set_loading(True)
        self._start_fetch(is_first_load=True)

    def toggle_pause(self):
        self.paused = not self.paused
        self.match_screen.set_paused(self.paused)
        if self.paused:
            self._cancel_poll()
        else:
            self._start_fetch()

    def select_innings(self, innings_number):
        self.innings_selected = innings_number
        self.innings_auto_selected = True
        self.match_screen.set_active_innings(innings_number)
        self._cancel_poll()
        self._start_fetch()

    def _cancel_poll(self):
        if self._poll_job is not None:
            self.after_cancel(self._poll_job)
            self._poll_job = None

    def _schedule_poll(self):
        self._cancel_poll()
        if not self.paused and self.game_id:
            self._poll_job = self.after(REFRESH_INTERVAL_MS, self._start_fetch)

    def _start_fetch(self, is_first_load=False):
        self._poll_job = None
        if not self.game_id or self.fetching_session == self.session_id:
            return  # nothing to load, or a request is already running

        session_id = self.session_id
        game_id = self.game_id
        requested_innings = self.innings_selected
        auto_select_innings = not self.innings_auto_selected
        self.fetching_session = session_id

        def fetch_in_background():
            try:
                snapshot = build_snapshot(game_id, requested_innings, auto_select_innings)
            except Exception:
                snapshot = None
            self._ui_queue.put(lambda: self._handle_snapshot(session_id, snapshot, is_first_load))

        threading.Thread(target=fetch_in_background, daemon=True).start()

    def _process_ui_queue(self):
        """Runs on the UI thread and applies results produced by the worker threads."""
        try:
            while True:
                pending_update = self._ui_queue.get_nowait()
                pending_update()
        except queue.Empty:
            pass
        self._queue_job = self.after(80, self._process_ui_queue)

    def _handle_snapshot(self, session_id, snapshot, is_first_load):
        if self.fetching_session == session_id:
            self.fetching_session = None
        if session_id != self.session_id:
            return  # the user has moved on to another game

        if snapshot is None:
            if is_first_load:
                self.landing_screen.set_loading(False)
                self.landing_screen.show_error("Couldn't load that game. Check the link/ID and your connection.")
            else:
                self.match_screen.set_message("Connection problem. Retrying...", is_error=True)
                self._schedule_poll()
            return

        if is_first_load:
            self.match_screen.reset(self.game_id)
            self.landing_screen.set_loading(False)
            self._show_screen(self.match_screen)

        # the user switched innings while this request was running, so fetch again
        if self.innings_auto_selected and snapshot["view_innings"] != self.innings_selected:
            self._start_fetch()
            return

        if not self.innings_auto_selected:
            self.innings_selected = snapshot["view_innings"]
            self.innings_auto_selected = True

        self.match_screen.show_snapshot(snapshot, self.innings_selected)
        self._schedule_poll()

    def on_close(self):
        self.session_id += 1
        self._cancel_poll()
        if self._queue_job is not None:
            self.after_cancel(self._queue_job)
        self.destroy()
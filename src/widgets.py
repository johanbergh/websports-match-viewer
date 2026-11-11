from tkinter import ttk
import customtkinter as ctk

from src.config import *

def initials(name):
    first_letters = "".join(word[0] for word in name.split()[:2])
    return first_letters.upper() or "?"

class TeamPanel(ctk.CTkFrame):
    """Logo (or initials), team name and score."""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        logo_holder = ctk.CTkFrame(self, fg_color="transparent", width=76, height=76)
        logo_holder.pack(pady=(0, 6))
        logo_holder.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(logo_holder, text="")
        self.initials_label = ctk.CTkLabel(logo_holder, text="", width=72, height=72, corner_radius=36, fg_color=CARD_ALT, text_color=MUTED, font=make_font(24, "bold"))

        self.name_label = ctk.CTkLabel(self, text="-", font=make_font(18, "bold"), text_color=TEXT, wraplength=260)
        self.name_label.pack()

        self.score_label = ctk.CTkLabel(self, text="-", font=make_font(36, "bold"), text_color=TEXT)
        self.score_label.pack(pady=(2, 0))

        self.overs_label = ctk.CTkLabel(self, text="", font=make_font(13), text_color=MUTED)
        self.overs_label.pack()

    def show_team(self, name, score, overs, logo_image):
        self.name_label.configure(text=name)
        self.score_label.configure(text=score)
        self.overs_label.configure(text=overs)

        self.logo_label.pack_forget()
        self.initials_label.pack_forget()
        if logo_image is not None:
            self.logo_label.configure(image=logo_image)
            self.logo_label.pack(expand=True)
        else:
            self.initials_label.configure(text=initials(name))
            self.initials_label.pack(expand=True)

class LiveCard(ctk.CTkFrame):
    """Small card listing up to two players with a stat on the right."""
    def __init__(self, master, heading):
        super().__init__(master, fg_color=CARD, corner_radius=16)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text=heading, font=make_font(11, "bold"), text_color=ACCENT).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(12, 4))

        # one (name label, stat label) pair per player line
        self.line_labels = []
        for line_number in range(2):
            name_label = ctk.CTkLabel(self, text="", font=make_font(14, "bold"), anchor="w", text_color=TEXT)
            stat_label = ctk.CTkLabel(self, text="", font=make_font(14), anchor="e", text_color=MUTED)
            is_last_line = line_number == 1
            vertical_padding = (0, 12) if is_last_line else (0, 2)
            name_label.grid(row=line_number + 1, column=0, sticky="ew", padx=(18, 8), pady=vertical_padding)
            stat_label.grid(row=line_number + 1, column=1, sticky="e", padx=(8, 18), pady=vertical_padding)
            self.line_labels.append((name_label, stat_label))

    def set_lines(self, lines):
        for line_number, (name_label, stat_label) in enumerate(self.line_labels):
            if line_number < len(lines):
                player_name, stat, is_active = lines[line_number]
                marker = "●" if is_active else "○" # to do: use actual unicode for optimisation
                name_label.configure(text=f"{marker}  {player_name}", text_color=ACCENT if is_active else TEXT)
                stat_label.configure(text=stat)
            elif line_number == 0:
                # nothing to show at all
                name_label.configure(text="-", text_color=MUTED)
                stat_label.configure(text="")
            else:
                name_label.configure(text="")
                stat_label.configure(text="")

class DataTable(ctk.CTkFrame):
    """Card containing a styled Treeview with a themed scrollbar."""
    def __init__(self, master, title, columns, has_footer=False, empty_text="No data yet"):
        super().__init__(master, fg_color=CARD, corner_radius=16)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._columns = columns
        self._empty_text = empty_text
        self._last_rows = None

        ctk.CTkLabel(self, text=title, font=make_font(15, "bold"), text_color=TEXT).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(14, 8))

        self.tree = ttk.Treeview(self, columns=[column[0] for column in columns], show="headings", style="Match.Treeview", selectmode="none", height=8)
        for column_id, heading, width, anchor, stretch in columns:
            self.tree.heading(column_id, text=heading, anchor=anchor)
            self.tree.column(column_id, width=width, minwidth=max(36, width // 2), anchor=anchor, stretch=stretch)

        self.tree.tag_configure("odd", background=CARD)
        self.tree.tag_configure("even", background=STRIPE)
        self.tree.tag_configure("notout", foreground=ACCENT)
        self.tree.tag_configure("empty", foreground=MUTED)

        scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview, fg_color=CARD, button_color=CARD_ALT, button_hover_color=ACCENT_DIM)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(14, 0), pady=(0, 12))
        scrollbar.grid(row=1, column=1, sticky="ns", padx=(4, 8), pady=(0, 12))

        self.footer_label = None
        if has_footer:
            self.footer_label = ctk.CTkLabel(self, text="", font=make_font(13), text_color=MUTED, anchor="w")
            self.footer_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 14))

    def set_rows(self, rows):
        # skip the redraw when nothing changed so the scroll position stays put
        if rows == self._last_rows:
            return
        self._last_rows = rows

        self.tree.delete(*self.tree.get_children())

        if not rows:
            empty_row = [""] * len(self._columns)
            # the batting table starts with a "#" column, so the message goes in the next one
            message_column = 1 if len(self._columns) > 4 else 0
            empty_row[message_column] = self._empty_text
            self.tree.insert("", "end", values=empty_row, tags=("odd", "empty"))
            return

        for row_number, (values, extra_tags) in enumerate(rows):
            stripe_tag = "even" if row_number % 2 else "odd"
            self.tree.insert("", "end", values=values, tags=(stripe_tag,) + tuple(extra_tags))

    def clear(self):
        self._last_rows = None
        self.tree.delete(*self.tree.get_children())

def ghost_button(master, text, command, width=100):
    """Outlined lime button used for Back and Pause."""
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=36,
        corner_radius=18, fg_color="transparent", border_width=2,
        border_color=ACCENT, text_color=ACCENT, hover_color=CARD_ALT,
        font=make_font(13, "bold"),
    )
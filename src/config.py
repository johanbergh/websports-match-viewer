import customtkinter as ctk

# how often the match screen refreshes (in milliseconds)
REFRESH_INTERVAL_MS = 10000

# values the API uses when a batsman has not been dismissed
NOT_OUT_VALUES = {"not out", "n/o", "notout", "not_out"}

# theme
FONT_FAMILY = "Segoe UI"

BG = "#020817"
CARD = "#0b1424"
CARD_ALT = "#0f1b30"
STRIPE = "#0e1a2e"
STATUS_BAR = "#050d1c"
ACCENT = "#b5e61d"
ACCENT_HOVER = "#9ac715"
ACCENT_DIM = "#8fb318"
BTN_TEXT = "#020817"
TEXT = "#e8eef7"
MUTED = "#8593a8"
DANGER = "#ff6b6b"

def make_font(size, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)
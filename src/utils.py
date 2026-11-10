import re

def extract_game_id(text):
    """Accepts a bare game ID or any websports URL containing 'gid'."""
    if not text:
        return None

    text = text.strip()
    if re.fullmatch(r"\d+", text):
        return text

    gid_match = re.search(r"[?&]gid=(\d+)", text)
    if gid_match:
        return gid_match.group(1)

    number_match = re.search(r"(\d{4,7})", text)
    return number_match.group(1) if number_match else None

def has_value(value):
    return value not in (None, "")

def get_result(fixture):
    """The match result text, or "" while the match is still being played."""
    result = str(fixture.get("result") or "").strip()
    if result.lower().replace(" ", "") in ("noton", "n/a"):
        return ""
    return result

def full_name(player):
    first_name = player.get("PlayerName", "")
    surname = player.get("PlayerSurname", "")
    return f"{first_name} {surname}".strip()

def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def overs_to_balls(overs):
    """'3.4' means 3 overs and 4 balls, so 22 balls."""
    try:
        whole_overs, _, extra_balls = str(overs).partition(".")
        return int(whole_overs or 0) * 6 + int(extra_balls or 0)
    except ValueError:
        return None

def has_batted(runs, wickets, overs):
    """True once a team has scored, lost a wicket or faced a ball (a score of 0 means they haven't batted yet)."""
    runs_scored = to_float(runs) or 0
    wickets_lost = to_float(wickets) or 0
    balls_faced = overs_to_balls(overs) or 0
    return runs_scored > 0 or wickets_lost > 0 or balls_faced > 0

def initials(name):
    first_letters = "".join(word[0] for word in name.split()[:2])
    return first_letters.upper() or "?"

def shorten(text, limit=22):
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"

def detect_live_innings(fixture):
    """Which innings is currently active (1 or 2), or None if the match is over."""
    team_a_batted = has_batted(fixture.get("aRuns"), fixture.get("aWickets"), fixture.get("aOvers"))
    team_b_batted = has_batted(fixture.get("bRuns"), fixture.get("bWickets"), fixture.get("bOvers"))
    match_over = bool(get_result(fixture))

    # once team B has batted, the second innings is the active one
    if team_b_batted:
        return None if match_over else 2

    if team_a_batted:
        return 1

    return None if match_over else 1
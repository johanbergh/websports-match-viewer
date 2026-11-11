import re
from api.client import *

def get_fixture(game_id):
    """The key match detais for a game."""
    fixture_response = get_json(f"getfixture/{game_id}/1")

    # checks if the request failed, returned empty data, or lacked the fixtures key
    if not fixture_response or not fixture_response.get("fixtures"):
        return None
    
    return fixture_response["fixtures"][0]

def extract_game_id(text):
    """Accepts a bare game ID or any websports URL containing 'gid'."""
    if not text:
        return None

    text = text.strip()
    # if the entire string is made of digits (like "12345"), return it directly
    if re.fullmatch(r"\d+", text):
        return text

    # look for a 'gid=' query parameter in a URL
    gid_match = re.search(r"[?&]gid=(\d+)", text)
    if gid_match:
        return gid_match.group(1) # return only the digits captured after 'gid='

    # search anywhere in the text for a 4- to 7-digit number / if the text is something like "jj 3441 hf" = 3441
    number_match = re.search(r"(\d{4,7})", text)

    # return the matched number if found
    return number_match.group(1) if number_match else None

def has_value(value):
    """Return True if value is neither None nor an empty string."""
    # Checks that the value is not missing (None) or blank ("")
    # Note: 0 and False will still return True
    return value not in (None, "")

def get_result(fixture):
    """The match result text, or "" while the match is still being played."""
    # Safely get the "result" field, default to "" if missing/None, and trim outer spaces
    result = str(fixture.get("result") or "").strip()

    # Normalize to lowercase without spaces to catch placeholders like "Not On", "noton", or "N/A"
    if result.lower().replace(" ", "") in ("noton", "n/a"):
        return ""

    # Return the cleaned match result text
    return result

def to_float(value):
    """Safely convert a value to a float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def overs_to_balls(overs):
    """'3.4' = 3 overs, 4 balls = 22 balls"""
    if overs is None:
        return None
    try:
        # assuming that the server always returns a "good" over value
        # 4.3 or 12.1 instead of 18.9 or 18.7
        parts = str(overs).split(".")
        whole_overs = int(parts[0])
        extra_balls = int(parts[1]) if len(parts) > 1 else 0
        return whole_overs * 6 + extra_balls
    except ValueError:
        return None

def has_batted(runs, wickets, overs):
    """True once a team has scored, lost a wicket, or faced a ball."""
    stats = (to_float(runs), to_float(wickets), overs_to_balls(overs))
    return any((value or 0) > 0 for value in stats)

def detect_live_innings(fixture):
    """Which innings is currently active (1 or 2), or None if the match is over."""
    # check if team A, team b (first inn, second inn) has recorded any stats
    team_a_batted = has_batted(fixture.get("aRuns"), fixture.get("aWickets"), fixture.get("aOvers"))
    team_b_batted = has_batted(fixture.get("bRuns"), fixture.get("bWickets"), fixture.get("bOvers"))

    # check if a final match result text exists (True if finished, False if still live/upcoming)
    match_over = bool(get_result(fixture))

    # once Team B has batted, the second innings is active unless the match has already ended
    if team_b_batted:
        return None if match_over else 2

    # if only Team A has batted so far, the first innings is still underway
    if team_a_batted:
        return 1

    # if neither team has batted yet (0/0), return None if abandoned/ended, or 1 if about to start
    return None if match_over else 1
import time
from concurrent.futures import ThreadPoolExecutor

from api import *
from src.config import NOT_OUT_VALUES

_executor = ThreadPoolExecutor(max_workers=7) # Pool of 7 worker threads so all 7 API/logo requests in build_snapshot run in parallel

def format_score(runs, wickets, overs):
    """Returns the big score text and the smaller overs text for a team."""
    # If the team hasn't batted or runs are missing, show a placeholder dash
    if not has_value(runs):
        return "-", ""

    # Format as "runs/wickets" if wickets exist, otherwise just "runs"
    score_text = f"{runs}/{wickets}" if has_value(wickets) else str(runs)
    # Append "overs" label if overs are recorded
    overs_text = f"{overs} overs" if has_value(overs) else ""

    return score_text, overs_text

def build_batting_rows(batting_response):
    """Formats batting scorecard entries into table rows with strike rates and not-out tags."""
    batting_rows = []
    if not batting_response or not batting_response.get("scorecard"):
        return batting_rows

    for batter in batting_response["scorecard"]:
        # use full name, falling back to initials if full name is blank
        name = full_name(batter) or batter.get("PlayerNameInitial", "")
        how_out_short = str(batter.get("HowOut", "") or "")
        how_out_full = str(batter.get("HowOutFull", "") or "")

        # determine if the batter is currently not out based on short code or full text
        is_not_out = (how_out_short.lower() in NOT_OUT_VALUES or how_out_full.lower().startswith("n/o"))
        how_out = "not out" if is_not_out else (how_out_full or how_out_short)

        # calculate strike rate (runs per 100 balls) if both runs and balls > 0 are valid
        runs = batter.get("BatRuns", "")
        balls = batter.get("BatBalls", "")
        runs_number = to_float(runs)
        balls_number = to_float(balls)
        if runs_number is not None and balls_number:
            strike_rate = f"{runs_number / balls_number * 100:.1f}"
        else:
            strike_rate = ""

        # add an asterisk (*) and a UI highlight tag ("notout") for batters still in
        display_name = name + (" *" if is_not_out else "")
        row_values = (batter.get("BattingNr", ""), display_name, runs, balls, batter.get("BatFours", ""), batter.get("BatSixes", ""), strike_rate, how_out)
        row_tags = ("notout",) if is_not_out else ()
        batting_rows.append((row_values, row_tags))

    return batting_rows

def build_extras_text(extras_response):
    """Formats the extras breakdown line (wides, no-balls, byes, leg-byes)."""
    if not extras_response or not extras_response.get("extras"):
        return "Extras -"

    extras = extras_response["extras"][0]
    return (
        f"Extras  {extras.get('Extras', 0)} "
        f"(w {extras.get('WideBalls', 0)}, "
        f"nb {extras.get('NoBalls', 0)}, "
        f"b {extras.get('Byes', 0)}, "
        f"lb {extras.get('LegByes', 0)})"
    )

def build_bowling_rows(bowling_response):
    """Formats bowling scorecard entries into table rows with calculated economy rates."""
    bowling_rows = []
    if not bowling_response or not bowling_response.get("scorecard"):
        return bowling_rows

    for bowler in bowling_response["scorecard"]:
        overs = bowler.get("OversBowled", 0)
        # skip players listed on the scorecard who have bowled 0 overs
        if str(overs) in ("0", "0.0"):
            continue

        # calculate economy rate (runs conceded per 6-ball over)
        runs_conceded = bowler.get("RunsAgainst", "")
        balls_bowled = overs_to_balls(overs)
        runs_number = to_float(runs_conceded)
        if runs_number is not None and balls_bowled:
            economy = f"{runs_number / (balls_bowled / 6):.2f}"
        else:
            economy = ""

        row_values = (full_name(bowler), overs, runs_conceded, bowler.get("Wickets", ""), economy)
        bowling_rows.append((row_values, ()))

    return bowling_rows

def build_crease_lines(current_batsmen_response):
    """The two batsmen currently in, as (name, 'runs (balls)', on_strike)."""
    crease_lines = []
    if not current_batsmen_response or not current_batsmen_response.get("batsmen"):
        return crease_lines

    # Take up to 2 active batters and flag who is currently facing (OnStrike)
    for batsman in current_batsmen_response["batsmen"][:2]:
        crease_lines.append((full_name(batsman), f"{batsman.get('BatRuns', 0)} ({batsman.get('BatBalls', 0)})", batsman.get("CurrentPlayer") == "OnStrike"))

    return crease_lines

def build_current_bowler_lines(current_bowlers_response, bowling_team_id):
    """The bowlers to show, as (name, 'wickets/runs (overs)', currently_bowling)."""
    bowler_lines = []
    if not current_bowlers_response or not current_bowlers_response.get("bowlers"):
        return bowler_lines

    all_bowlers = current_bowlers_response["bowlers"]
    # filter to the active bowling team, falling back to all bowlers if TeamID is missing
    team_bowlers = [b for b in all_bowlers if b.get("TeamID") == bowling_team_id]
    candidates = team_bowlers or all_bowlers

    # prefer bowlers actively marked "BowlOn" (current and other-end bowler)
    bowling_now = [b for b in candidates if b.get("CurrentPlayer") == "BowlOn"][:2]
    if not bowling_now:
        # nobody tagged as currently bowling, so fall back to whoever has bowled previously
        bowling_now = [b for b in candidates if str(b.get("OversBowled", 0)) not in ("0", "0.0")][:2]

    for bowler in bowling_now:
        figures = f"{bowler.get('Wickets', 0)}/{bowler.get('RunsAgainst', 0)} ({bowler.get('OversBowled', '')})"
        bowler_lines.append((full_name(bowler), figures, bowler.get("CurrentPlayer") == "BowlOn"))

    return bowler_lines

def build_status_text(fixture):
    """Returns the live chase requirement text, or the final match result if finished."""
    status = fixture.get("RunsRequired")

    # no chase to report (the API sends "NotOn"), so show the match result if there is one
    if str(status or "").lower().replace(" ", "") in ("", "noton"):
        result = get_result(fixture)
        if result:
            status = result

    return status

def build_snapshot(game_id, requested_innings, auto_select_innings):
    """Fetches everything the match screen needs and returns it ready to be displayed."""
    fixture = get_fixture(game_id)
    if fixture is None:
        return None

    # extract team IDs, display names, and batting state
    team_a_id = fixture.get("aTeamID")
    team_b_id = fixture.get("bTeamID")
    team_a_name = fixture.get("aTeam") or "Team A"
    team_b_name = fixture.get("bTeam") or "Team B"
    team_a_runs = fixture.get("aRuns")
    team_b_runs = fixture.get("bRuns")
    team_b_batted = has_batted(team_b_runs, fixture.get("bWickets"), fixture.get("bOvers"))

    live_innings = detect_live_innings(fixture)

    # decide which innings scorecard to show (auto-follow live play or use manual tab selection)
    if auto_select_innings:
        if live_innings in (1, 2):
            viewed_innings = live_innings
        else:
            viewed_innings = 2 if team_b_batted else 1
    else:
        viewed_innings = requested_innings

    # assign batting and bowling team IDs for the scorecard the user is viewing
    if viewed_innings == 1:
        viewed_batting_team_id, viewed_bowling_team_id = team_a_id, team_b_id
    else:
        viewed_batting_team_id, viewed_bowling_team_id = team_b_id, team_a_id

    # assign batting and bowling team IDs for the live "at the crease" cards
    if live_innings == 1:
        live_batting_team_id, live_bowling_team_id = team_a_id, team_b_id
    elif live_innings == 2:
        live_batting_team_id, live_bowling_team_id = team_b_id, team_a_id
    else:
        live_batting_team_id = team_b_id if team_b_batted else team_a_id
        live_bowling_team_id = team_a_id if live_batting_team_id == team_b_id else team_b_id

    # fire all 7 network/image requests concurrently instead of sequentially
    submit = _executor.submit
    batting_future = submit(get_batting_scorecard, game_id, viewed_batting_team_id)
    extras_future = submit(get_extras, game_id, viewed_batting_team_id)
    bowling_future = submit(get_bowling_scorecard, game_id, viewed_bowling_team_id)
    current_batsmen_future = submit(get_current_batsmen, game_id, live_batting_team_id)
    current_bowlers_future = submit(get_current_bowlers, game_id)
    team_a_logo_future = submit(get_logo, fixture.get("aLogoName"))
    team_b_logo_future = submit(get_logo, fixture.get("bLogoName"))

    # wait for all futures to finish and assemble the complete UI data dictionary
    return {
        "title": fixture.get("game", "") or "",
        "status": build_status_text(fixture),
        "view_innings": viewed_innings,
        "team_a": team_a_name,
        "team_b": team_b_name,
        "score_a": format_score(team_a_runs, fixture.get("aWickets"), fixture.get("aOvers")),
        "score_b": format_score(team_b_runs, fixture.get("bWickets"), fixture.get("bOvers")),
        "logo_a": (fixture.get("aLogoName"), team_a_logo_future.result()),
        "logo_b": (fixture.get("bLogoName"), team_b_logo_future.result()),
        "batting_rows": build_batting_rows(batting_future.result()),
        "extras": build_extras_text(extras_future.result()),
        "bowling_rows": build_bowling_rows(bowling_future.result()),
        "crease": build_crease_lines(current_batsmen_future.result()),
        "bowlers": build_current_bowler_lines(current_bowlers_future.result(), live_bowling_team_id),
        "updated": time.strftime("%H:%M:%S"),
    }
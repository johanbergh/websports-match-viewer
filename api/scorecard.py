from api.client import get_json

# note: innings_id is set to 1 by default since websports uses the standard innings numbering
# thus, the current code won't be able to return the second innings if the match is double innings
# to do: well, make it work double innings later
def get_batting_scorecard(game_id, team_id, innings_id=1):
    return get_json(f"fixture/scorecard/batting/{game_id}/{team_id}/{innings_id}")

def get_bowling_scorecard(game_id, team_id, innings_id=1):
    return get_json(f"fixture/scorecard/bowling/{game_id}/{team_id}/{innings_id}")

def get_extras(game_id, team_id, innings_id=1):
    return get_json(f"fixture/scorecard/extras/{game_id}/{team_id}/{innings_id}")
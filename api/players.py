from api.client import get_json

# note: innings_id is set to 1 by default since websports uses the standard innings numbering
# thus, the current code won't be able to return the second innings if the match is double innings
# to do: well, make it work double innings later
def get_current_batsmen(game_id, batting_team_id, innings_id=1):
    return get_json(f"fixture/batsmen/{game_id}/{batting_team_id}/{innings_id}")

def get_current_bowlers(game_id, innings_id=1):
    return get_json(f"fixture/bowlers/{game_id}/{innings_id}")

def full_name(player):
    first_name = player.get("PlayerName", "")
    surname = player.get("PlayerSurname", "")
    return f"{first_name} {surname}".strip()
import json

def load_all_teams_from_json_into_dict(json_file_path="data/all_teams_stratz.json"):
    """
    Load all teams from a JSON file into a dictionary.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            #convert to team dictionary
            teams_dict = {}
            for team in data:
                teams_dict[team['tid']] = team
            return teams_dict
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")

def calculate_mmr_from_teams_played(pid, mode="max"):
    """
    Calculate MMR from teams played by the player.
    """
    #find player
    players = load_all_players_dict_from_json_stratz()
    player = players[pid]
    
    #load all teams played by the player
    player_tids = player['player_teams_ids']

    #load all teams dict from json
    teams = load_all_teams_from_json_into_dict()

    #calculate average mmr of all teams played by the player
    player_team_list = [teams[tid]['team_mmr'] for tid in player_tids]
    if mode == "avg":
        mmr = round(sum(player_team_list) / len(player_team_list),2) 
    elif mode == "max":
        mmr = max(player_team_list)
    return mmr

def load_all_players_dict_from_json_stratz(json_file_path="data/all_players_stratz.json"):
    """
    Load all players from a JSON file.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            #convert to player dictionary
            players_dict = {}
            for player in data:
                #hack fix later
                player['reliable_mmr'] = True
                players_dict[player['pid']] = player
            return players_dict
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")

def load_all_matches_from_json(json_file_path="data/all_matches.json"):
    """
    Load all matches from a JSON file.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")

def load_team_mmr_from_json(self, json_file_path="data/player_team_mmr.json"):
    """
    Load team MMR for the player from a JSON file.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            if self.pid in data:
                return data[self.pid]['mmr']
            else:
                print(f"Player ID {self.pid} not found in {json_file_path}")
                return None
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")

def load_all_teams_from_json(json_file_path="data/all_teams.json"):
    """
    Load all teams from a JSON file.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")

def load_team_mmr_from_json(json_file_path="data/player_team_mmr.json"):
    """
    Load team MMR from a JSON file.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")

def load_all_players_from_json(json_file_path="data/all_players.json"):
    """
    Load all players from a JSON file.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")


def search_level_by_team(team):
    """
    Search the level of a team by its name.
    """
    teams = load_all_teams_from_json()
    for t in teams:
        if t['team_name'] == team:
            return t['level']
    return None
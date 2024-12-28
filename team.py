import json
import mysql.connector
from db_utils import query_db, print_query_results
from utils import load_all_teams_from_json

class Team:
    """
    Represents a team in the AD2L database.
    """
    def __init__(self, tid: str, team_name: str = "Undefined", team_players: set = None, team_players_ids: set = None,matches: list = None, team_mmr: float = 0):
        """
        """
        self.tid = tid
        self.team_name = team_name
        self.team_players = team_players if team_players is not None else set()
        self.team_players_ids = team_players_ids if team_players_ids is not None else set()
        self.matches = matches
        self.team_mmr = team_mmr

    def to_dict(self):
        return {
            'tid': self.tid,
            'team_name': self.team_name,
            'team_mmr': self.team_mmr,
            'team_players': list(self.team_players),
            'team_players_ids': list(self.team_players_ids),
            'matches': self.matches
        }
    
    def print_team(self):
        print(f"Team ID: {self.tid}")
        print(f"Team Name: {self.team_name}")
        print(f"Team Players: {self.team_players}")
        print(f"Team MMR: {self.team_mmr}")
        print(f"Matches: {self.matches}")

def load_all_teams_dict(json_file_path="data/all_teams.json"):
    """
    Load all teams from a JSON file into list of team objects.
    """
    team_json_list = load_all_teams_from_json(json_file_path)
    team_dict = {}

    for team in team_json_list:
        team_dict[team['tid']] = (Team(team['tid'], team['team_name'], team['team_players'], team['matches']))
    
    return team_dict

if __name__ == "__main__":
    teams = load_all_teams_from_json()

    for team in teams:
        if "Twink" in team['team_name']:
            print(team)


        
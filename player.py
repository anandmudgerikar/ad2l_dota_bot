#Player Class
import json
from utils import load_all_players_from_json, load_team_mmr_from_json
from db_utils import get_player_ranks_from_league_graph_query
import tenacity

class Player:
    """
    Player class
    """

    def __init__(self, pid: str, player_name: str = "Undefined", player_teams: set = None, player_teams_ids: set = None, matches: list = None, mmr: float = 0, reliable_mmr: bool=True):
        """
        """
        self.pid = pid
        self.player_name = player_name
        self.player_teams = player_teams if player_teams is not None else set()
        self.player_teams_ids = player_teams_ids if player_teams_ids is not None else set()
        self.matches = matches if matches is not None else []
        self.reliable_mmr = reliable_mmr

        #initiate player team mmr based on highest level of team played by them
        self.team_mmr = self.get_team_mmr()
        
        self.mmr = self.get_initial_mmr_stratz()*100
    
    def to_dict_for_printing(self):
        return {
            'pid': self.pid,
            'player_name': self.player_name,
            'player_teams': list(self.player_teams),
            'matches': len(self.matches),
            'team_mmr': self.team_mmr,
            'mmr': self.mmr,
            'reliable_mmr': self.reliable_mmr,
        }

    def to_dict(self):
        return {
            'pid': self.pid,
            'player_name': self.player_name,
            'player_teams': list(self.player_teams),
            'player_teams_ids': list(self.player_teams_ids),
            'matches': self.matches,
            'team_mmr': self.team_mmr,
            'mmr': self.mmr,
            'reliable_mmr': self.reliable_mmr,
        }
    
    def get_initial_mmr_stratz(self):
        """
        Get initial MMR from Stratz API.
        """

        ranks = get_player_ranks_from_league_graph_query(self.pid)['data']['player']['ranks']

        if not ranks:
            print(f"Player ID {self.pid} not found in Stratz API")
            return 0

        highest_mmr = 0
        for rank in ranks:
            if rank:
                highest_mmr = max(highest_mmr,rank['rank'])
                
        print(highest_mmr)

        return highest_mmr

    def get_team_mmr(self):
        """
        Get team team MMR for the player.
        """
        team_mmr = load_team_mmr_from_json()
        if str(self.pid) in team_mmr:
            return team_mmr[str(self.pid)]['mmr']
        else:
            print(f"Player ID {self.pid} not found in team MMR data")
            return None 

def load_all_players_dict(json_file_path="data/all_players.json"):
    """
    Load all players from a JSON file into list of player objects.
    """
    player_json_list = load_all_players_from_json(json_file_path)
    player_dict = {}

    for player in player_json_list:
        player_dict[player['pid']] = (Player(player['pid'], player['player_name'], player['player_teams'], player['matches'], player['mmr']))
    
    return player_dict

def load_all_players_dict_stratz(json_file_path="data/all_players_stratz.json"):
    """
    Load all players from a JSON file into list of player objects.
    """
    pass
    
if __name__ == "__main__":
    player = Player("39092")
    print(player.team_mmr)

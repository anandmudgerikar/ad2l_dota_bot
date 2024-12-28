import json

class Match:
    """
    Match class
    """

    def __init__(self, match_id: str, steam_match_id: str="Undefined",home_team: str = "Undefined", home_team_id: str = "Undefined", away_team: str = "Undefined", away_team_id: str = "Undefined", home_score: int = 0, away_score: int = 0, league_id: str = "Undefined", d2_match_ids: list = None, match_date: str = "Undefined", level: int = 0, ht_players: list = [], at_players: list = []): 
        """
        """
        self.match_id = match_id
        self.home_team = home_team
        self.home_team_id = home_team_id
        self.away_team = away_team
        self.away_team_id = away_team_id
        self.home_score = home_score if home_score is not None else 0
        self.away_score = away_score if away_score is not None else 0
        self.league_id = league_id
        self.d2_match_ids = d2_match_ids
        self.match_date = match_date
        self.steam_match_id = steam_match_id
        self.level = level
        self.ht_players = ht_players
        self.at_players = at_players
    
    def to_dict(self):
        return {
            'match_id': self.match_id,
            'steam_match_id': self.steam_match_id,
            'league_id': self.league_id,
            'home_team_id': self.home_team_id,
            'home_team': self.home_team,
            'away_team_id': self.away_team_id,
            'away_team': self.away_team,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'match_date': self.match_date,
            'level': self.level,
            'ht_players': self.ht_players,
            'at_players': self.at_players,
        }
    
    def print_match(self):
        print(f"Match ID: {self.match_id}")
        print(f"Steam Match ID: {self.steam_match_id}")
        print(f"League ID: {self.league_id}")
        print(f"Home Team: {self.home_team}")
        print(f"Away Team: {self.away_team}")
        print(f"Home Score: {self.home_score}")
        print(f"Away Score: {self.away_score}")
        print(f"Match Date: {self.match_date}")
        print(f"Level: {self.level}")
        print(f"Home Team Players: {self.ht_players}")
        print(f"Away Team Players: {self.at_players}")
    

def main():
    matches = Match.load_all_matches_from_json()

    for match in matches:
        if match['steam_match_id']:
            print(match)

if __name__ == "__main__":
    main()
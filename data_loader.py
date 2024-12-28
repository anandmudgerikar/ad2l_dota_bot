from db_utils import query_db, print_query_results, get_matches_from_league_graph_query
from utils import load_all_matches_from_json, load_all_teams_from_json, load_all_players_dict_from_json_stratz
from constants import league_levels, league_ids_stratz
from match import Match
from player import Player
from team import Team
import json

def generate_team_id2name_dict():
    """
    Generate team name to team id dictionary.
    """
    matches = load_all_matches_from_json(json_file_path="data/all_matches_stratz.json")
    team_id2name = {}

    for match in matches:
        home_team = match['home_team']
        home_team_id = match['home_team_id']
        away_team = match['away_team']
        away_team_id = match['away_team_id']

        team_id2name[home_team_id] = home_team
        team_id2name[away_team_id] = away_team
    
    return team_id2name

def load_all_teams_stratz():
    """
    Load all teams into a JSON file using Stratz API.(indirectly)
    """
    matches = load_all_matches_from_json(json_file_path="data/all_matches_stratz.json")
    players = load_all_players_dict_from_json_stratz(json_file_path="data/all_players_stratz.json")
    team_id2name = generate_team_id2name_dict()
    teams = {}

    for player in players.values():
        pid = player['pid']
        player_name = player['player_name']
        player_teams_ids = player['player_teams_ids']
        player_teams = player['player_teams']
        match_ids = player['matches']

        # print(f"Player: {player_name} played for {len(player_teams)} teams: {player_teams}")
        # print(f"Player: {player_name} played for {len(player_teams_ids)} teams: {player_teams_ids}")
        # print(f"Player: {player_name} played {len(match_ids)} matches: {match_ids}")

        for team_id in player_teams_ids:
            
            team_name = team_id2name[team_id]               
            
            if team_id not in teams:
                teams[team_id] = Team(tid=team_id,team_name=team_name,team_players=set([player_name]),team_players_ids=set([pid]))
            else:
                teams[team_id].team_players.add(player_name)
                teams[team_id].team_players_ids.add(pid)
    
    #assign team mmr based on average of all players that have played in the team
    for tid in teams:
        team_players = teams[tid].team_players_ids
        team_mmr = sum([players[player_id]['mmr'] for player_id in team_players])/len(team_players)
        teams[tid].team_mmr = team_mmr

    # Save teams as JSON
    with open('data/all_teams_stratz.json', 'w') as fp:
        json.dump([team.to_dict() for team in teams.values()], fp)

def get_leagues(start_season=38,end_season=42):
    
    #get all the players and initialize base rank according to max league they played in
    league_ids = range(start_season,end_season+1)

    #get normal season and playoff league ids
    ad2l_league_titles = [f"S{league_id} {league_level}" for league_id in league_ids for league_level in league_levels]
    ad2l_league_titles += [f"{league} Playoffs" for league in ad2l_league_titles]
    #print(ad2l_league_titles)
    
    query = f"""
            select id,title from seasons where title in {tuple(ad2l_league_titles)} 
                
    """
    league_ids = query_db(query)
    #print(league_ids)
    return league_ids

def generate_league_id2level_dict(league_ids):
    #storing league_id to level mapping
    league_id2level_dict = {}
    for league_id in league_ids:
        level = league_levels[league_id['title'].split(" ")[1]]
        league_id2level_dict[league_id['id']] = level
    return league_id2level_dict  


def load_all_players_into_json_stratz():
    """
    Load all players into a JSON file using Stratz API."""
    league_ids = list(league_ids_stratz.values())
    #print(league_ids)
    all_players = {}

    for league_id in league_ids:
        matches = get_matches_from_league_graph_query(league_id)['data']['league']['matches']
        
        #parse match data into Match objects
        
        for match in matches:
            
            home_team_id=match['radiantTeam']['id']
            home_team=match['radiantTeam']['name']
            away_team_id=match['direTeam']['id']
            away_team=match['direTeam']['name']

            for player in match['players']:
                #print(player)

                if player['isRadiant']:
                    player_team_id = home_team_id
                    player_team = home_team
                else:
                    player_team_id = away_team_id
                    player_team = away_team
            
                if player['steamAccount']['id'] not in all_players:
                    player_obj = Player(
                        pid=player['steamAccount']['id'],
                        player_name=player['steamAccount']['name'],
                        player_teams= set([player_team]),
                        player_teams_ids= set([player_team_id]),
                        matches=[match['id']]
                    )
                    all_players[player['steamAccount']['id']] = player_obj
                else:
                    all_players[player['steamAccount']['id']].player_teams.add(player_team)
                    all_players[player['steamAccount']['id']].player_teams_ids.add(player_team_id)
                    all_players[player['steamAccount']['id']].matches.append(match['id'])

    #save players as json
    with open('data/all_players_stratz.json', 'w') as fp:
        json.dump([player.to_dict() for player in all_players.values()], fp)

#todo: Currently querying for each player, need to optimize
def load_all_player_ranks_stratz():
    """
    Load all player ranks (highest rank ever in ranked mm) into a JSON file using Stratz API.
    """
    pass

def load_all_matches_into_json_stratz():
    """
    Load all matches into a JSON file using Stratz API.
    """
    league_ids = list(league_ids_stratz.values())
    #print(league_ids)
    all_matches = []

    for league_id in league_ids:
        matches = get_matches_from_league_graph_query(league_id)['data']['league']['matches']
        
        #parse match data into Match objects
        
        for match in matches:
            
            ht_players = []
            at_players = []

            for player in match['players']:
                print(player)
                if player['isRadiant']:
                    ht_players.append(player['steamAccount']['id'])
                else:
                    at_players.append(player['steamAccount']['id'])
            
            match_obj = Match(
                match_id= match['id'],
                steam_match_id= match['id'],
                league_id=league_id,
                home_score=1 if match['didRadiantWin'] else 0,
                away_score=1 if not match['didRadiantWin'] else 0,
                home_team_id=match['radiantTeam']['id'],
                home_team=match['radiantTeam']['name'],
                away_team_id=match['direTeam']['id'],
                away_team=match['direTeam']['name'],
                ht_players=ht_players,
                at_players=at_players,
                )
            
            #todo: get match level, skipping and using highest mmr of player for now
            # match_obj.level = max(search_level_by_team(match_obj.home_team), searcg_level_by_team(match_obj.away_team))
            all_matches.append(match_obj)
            match_obj.print_match()
            
    #save matches as json
    with open('data/all_matches_stratz.json', 'w') as fp:
        json.dump([match.to_dict() for match in all_matches], fp)        

def load_all_matches_into_json():
    """
    Load all matches into a JSON file using AD2l database.
    """ 
    #get all the players and initialize base rank according to max league they played in
    league_ids = get_leagues()
    #generate league_id to level dictionary
    league_id2level_dict = generate_league_id2level_dict(league_ids)

    #create league_ids string for query
    league_ids = [str(league_id['id']) for league_id in league_ids]
    league_ids_str = ",".join(league_ids)
    
    #get all matches and scores from these leagues
    query = f"""
            select m.id 'AD2L Match Id',m.steam_match_id 'Steam Match ID',m.season_id 'Season ID', ht.id 'HAID', ht.name 'Home Team', at.id 'AID',at.name 'Away Team', m.home_score 'Home Score', m.away_score 'Away Score', m.date 'Date' from matches m
            inner join teams ht on m.home_participant_id = ht.id
            inner join teams at on m.away_participant_id = at.id
            inner join seasons s on m.season_id = s.id
            where m.season_id in ({league_ids_str});
    """
    #print_query_results(query)
    matches = query_db(query)
    #print(matches)
    
    #parse match data into Match objects
    all_matches = []
    for match in matches:
        match_obj = Match(
            match_id=match['AD2L Match Id'],
            steam_match_id=match['Steam Match ID'],
            league_id=match['Season ID'],
            home_team_id=match['HAID'],
            home_team=match['Home Team'],
            away_team_id=match['AID'],
            away_team=match['Away Team'],
            home_score=match['Home Score'],
            away_score=match['Away Score'],
            match_date=match['Date'].strftime("%Y-%m-%d %H:%M:%S"),
            level = league_id2level_dict[match['Season ID']]
        )
        #print(match_obj)
        #print(match_obj.home_team_id)
        #print(match_obj.away_team_id)
        #print(match_obj.home_score)
        #print(match_obj.away_score)

        all_matches.append(match_obj)

    #save matches as json
    with open('data/all_matches.json', 'w') as fp:
        json.dump([match.to_dict() for match in all_matches], fp)

def load_all_teams_into_json():
    """
    Load all teams into a JSON file.
    """
    # Get all matches first
    matches = load_all_matches_from_json()
    teams = {}

    for match in matches:
        home_team = match['home_team']
        home_team_id = match['home_team_id']
        away_team = match['away_team']
        away_team_id = match['away_team_id']

        if home_team_id not in teams:
            teams[home_team_id] = Team(tid=home_team_id, team_name=home_team)
        
        if away_team_id not in teams:
            teams[away_team_id] = Team(tid=away_team_id, team_name=away_team)

    # Get team to player mapping
    team2player_dict = {}
    teams_str = ",".join([str(team_id) for team_id in teams.keys()])
    query = f"""SELECT DISTINCT team_id, player_id FROM players_teams WHERE team_id IN ({teams_str});"""
    team2player = query_db(query)

    for t2p in team2player:
        team_id = t2p['team_id']
        player_id = t2p['player_id']
        
        if team_id not in team2player_dict:
            team2player_dict[team_id] = [player_id]
        else:
            team2player_dict[team_id].append(player_id)

    for team_id, team in teams.items():
        team.team_players = team2player_dict.get(team_id, [])

    # Save teams as JSON
    with open('data/all_teams.json', 'w') as fp:
        json.dump([team.to_dict() for team in teams.values()], fp)
    

def load_all_players_into_json():
    """
    Load all players into a JSON file.
    """ 
    #first get all teams that have played in this league
    teams = load_all_teams_from_json()
    players = {}

    for team in teams:
        team_players = team['team_players']

        for player_id in team_players:
            if player_id not in players:
                players[player_id] = Player(pid=player_id)
    
    for player_id, player in players.items():
        for team in teams:
            if player_id in team['team_players']:
                if player.player_teams is None:
                    player.player_teams = [team['tid']]
                else:
                    player.player_teams.append(team['tid'])

    player_ids_str = ",".join([str(player_id) for player_id in players.keys()])
    query = f"""SELECT distinct id, name FROM players WHERE id IN ({player_ids_str});"""
    player_names = query_db(query)

    for player_name in player_names:
        player_id = player_name['id']
        player_name = player_name['name']
        players[player_id].player_name = player_name

    # Save players as JSON
    with open('data/all_players.json', 'w') as fp:
        json.dump([player.to_dict() for player in players.values()], fp)

#fix this
def load_team_mmr():

    #get all the players and initialize base rank according to max league they played in
    league_ids = get_leagues()
    #generate league_id to level dictionary
    league_id2level_dict = generate_league_id2level_dict(league_ids)

    #create league_ids string for query
    league_ids = [str(league_id['id']) for league_id in league_ids]
    league_ids_str = ",".join(league_ids)
    
    #get all matches and scores from these leagues
    query = f"""
            select m.season_id, ht.id 'HAID', ht.name 'Home Team', at.id 'AID',at.name 'Away Team', m.home_score 'Home Score', m.away_score 'Away Score' from matches m
            inner join teams ht on m.home_participant_id = ht.id
            inner join teams at on m.away_participant_id = at.id
            inner join seasons s on m.season_id = s.id
            where m.season_id in ({league_ids_str});
    """
    #print_query_results(query)
    matches = query_db(query)
    #print(matches)

    # team_names = set()
    # #get all teams from these leagues
    # for match in matches:
    #     if match['Home Team'] not in team_names:
    #         team_names.add(match['Home Team'])
    #     if match['Away Team'] not in team_names:
    #         team_names.add(match['Away Team'])

    #get all team ids from these leagues
    team_ids = set()
    team2league_dict = {}
    
    for match in matches:
        team_ids.add(match['HAID'])
        team_ids.add(match['AID'])

        if match['HAID'] in team2league_dict:
            team2league_dict[match['HAID']].append(match['season_id'])
        else:
            team2league_dict[match['HAID']] = [match['season_id']]
        
        if match['AID'] in team2league_dict:
            team2league_dict[match['AID']].append(match['season_id'])
        else:
            team2league_dict[match['AID']] = [match['season_id']]

    print(len(team_ids))
    
    #get all players from these teams
    query = f"""
            select distinct player_id from players_teams pt
            inner join players p on p.id = pt.player_id
            where pt.team_id in {tuple(team_ids)};
    """
    player_ids = query_db(query)
    #print_query_results(query)
    print(len(player_ids))

    player_ids = [str(player_id['player_id']) for player_id in player_ids]
    player_ids_str = ",".join(player_ids)

    #creating player team dictionary
    player_team_dict = {}
    query = f"""
            select distinct player_id,team_id from players_teams
            where player_id in ({player_ids_str});
    """
    player_teams = query_db(query)
    #print_query_results(query)

    for player_team in player_teams:
        if player_team['player_id'] in player_team_dict:
            player_team_dict[player_team['player_id']].append(player_team['team_id'])
        else:
            player_team_dict[player_team['player_id']] = [player_team['team_id']]
    
    #print(player_team_dict)
    #print(player_team_dict[34706])

    #initiate player rankings based on highest level of league played by them
    player_rankings = {}
    for player_id in player_ids:

        # if player_id != '39092':
        #     continue

        #find max league level played by player
        teams = player_team_dict[int(player_id)]
        #removing teams not in teams list (teams_ids)
        teams = [team for team in teams if team in team_ids]
        print(f"Player has played for {len(teams)} teams: {teams}")

        max_level = 0
        for team in teams:
            print(f"Played for team: {team}")
            team_seasons = team2league_dict[team]
            team_seasons = list(set(team_seasons))
            print(f"team_seasons: {team_seasons}")
            #print(league_id2level_dict)
            #print(team)
            team_seasons = [league_id2level_dict[team_season] for team_season in team_seasons]
            print(team_seasons)
            max_level = max(max_level,max(team_seasons))
            print(max_level)
        
        player_rankings[player_id] = {"mmr": max_level*1000, "id": player_id}

    print(player_rankings['39092'])            
    # #get all players from these leagues
    # query = f"""
    #         select distinct player_id from matches where league_id in {tuple(league_ids)}
    # """
    # player_ids = query_db(query)
    # print_query_results(query)

    #save player rankings as json
    import json
    with open('data/player_team_mmr.json', 'w') as fp:
        json.dump(player_rankings, fp)

if __name__ == "__main__":
    load_all_teams_stratz()
from db_utils import query_db, print_query_results

def init_rankings():

    #first get all the players and initialize base rank according to max league they played in
    league_ids = range(38,43)

    league_levels = {
        "Voyager": 1,
        "Explorer": 2,
        "Challenger": 3,
        "Warrior": 4,
        "Conqueror": 5,
        "Champion": 6,
        "Heroic": 7,
    }

    
    #get normal season and playoff league ids
    ad2l_league_titles = [f"S{league_id} {league_level}" for league_id in league_ids for league_level in league_levels]
    ad2l_league_titles += [f"{league} Playoffs" for league in ad2l_league_titles]
    #print(ad2l_league_titles)
    
    query = f"""
            select id,title from seasons where title in {tuple(ad2l_league_titles)} 
                
    """
    league_ids = query_db(query)
    #print(league_ids)
    
    #storing league_id to level mapping
    league_id2level_dict = {}
    for league_id in league_ids:
        level = league_levels[league_id['title'].split(" ")[1]]
        league_id2level_dict[league_id['id']] = level

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
    init_rankings()
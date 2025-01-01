from utils import load_all_matches_from_json, load_all_teams_from_json, load_all_players_dict_from_json_stratz, calculate_mmr_from_teams_played
from player import Player, load_all_players_dict
from team import Team, load_all_teams_dict
import json
import pandas as pd
from tabulate import tabulate
from constants import MINMATCHES, MAXK, MAXMATCHES, MINK

#clean up after figuring out the best K value and other parameters - this is a work in progress
#try tiered k values based on match avg mmr
#try different k values for playoffs and regular season
def calculate_elo_rating(R_A, R_B, S_A, player_game_count=25, match_confidence=1):
    """
    Calculate new Elo rating for a player based on the Elo rating system.
    """
    # if player_game_count < 20:
    #     K = 200
    # elif player_game_count < 40:
    #     K = 100
    # else:
    #     K = 50

    #calculating K value based on match mmr confidence
    rank_confidence = min(player_game_count/MAXMATCHES,1.0)
    K = MINK + ((MAXK-MINK)*match_confidence) #*rank_confidence
    
    print(f"K value: {K}")

    # Calculate expected scores
    E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
    E_B = 1 / (1 + 10 ** ((R_A - R_B) / 400))

    # Calculate new ratings
    R_A_new = R_A + K * (S_A - E_A)
    R_B_new = R_B + K * ((1 - S_A) - E_B)  # S_B = 1 - S_A

    return R_A_new

# #This is through teams and not accurate, reflects more team mmr than player mmr. Error source is lack of player-match data in ad2l database (players of old team are not stored, only current team is stored)
# def generate_player_rankings():

#     #get all matches in the league
#     matches = load_all_matches_from_json()
#     #print(len(matches))

#     #sort matches by id
#     matches = sorted(matches, key=lambda x: x['match_id'])

#     #get all teams in the league
#     teams = load_all_teams_dict()

#     #get all player ids
#     players = load_all_players_dict()

#     #replay through all matches to update mmr
#     count = 0
#     for match in matches:
#             count += 1
#             # Find teams
#             home_team_id = match['home_team_id']
#             home_team_name = teams[home_team_id].team_name
#             away_team_id = match['away_team_id']
#             away_team_name = teams[away_team_id].team_name
#             home_score = match['home_score']
#             away_score = match['away_score']

#             print(f"Match: {count} {home_team_name} vs {away_team_name} {home_score} - {away_score}")

#             # Find players in teams
#             ht_players = teams[home_team_id].team_players
#             at_players = teams[away_team_id].team_players

#             # Calculate average MMR for each team
#             ht_avg_mmr = sum(players[player].mmr for player in ht_players) / len(ht_players)
#             at_avg_mmr = sum(players[player].mmr for player in at_players) / len(at_players)

#             # MMR of all players before games
#             print("Before:")
#             print("=" * 40)
#             print(f"Home Team: {home_team_name}")
#             print("-" * 40)
#             for player in ht_players:
#                 print(f"{players[player].player_name:<20} MMR: {players[player].mmr}")
#             print("=" * 40)
#             print(f"Away Team: {away_team_name}")
#             print("-" * 40)
#             for player in at_players:
#                 print(f"{players[player].player_name:<20} MMR: {players[player].mmr}")
#             print("=" * 40)

#             # Update MMR for each player
#             for player in ht_players:
#                 score = (home_score - away_score)/2 if home_score > away_score else 0
#                 players[player].mmr = round(calculate_elo_rating(players[player].mmr, at_avg_mmr, score),2)
#             for player in at_players:
#                 score = (away_score - home_score)/2 if away_score > home_score else 0
#                 players[player].mmr = round(calculate_elo_rating(players[player].mmr, ht_avg_mmr,score),2)

#             # MMR of all players after games
#             print("After:")
#             print("=" * 40)
#             print(f"Home Team: {home_team_name}")
#             print("-" * 40)
#             for player in ht_players:
#                 print(f"{players[player].player_name:<20} MMR: {players[player].mmr}")
#             print("=" * 40)
#             print(f"Away Team: {away_team_name}")
#             print("-" * 40)
#             for player in at_players:
#                 print(f"{players[player].player_name:<20} MMR: {players[player].mmr}")
#             print("=" * 40)
    
#     return players

#     # # Save updated player MMRs to JSON
#     # with open('data/all_players_updatedmmr.json', 'w') as file:
#     #     json.dump([player.to_dict() for player in players.values()], file, indent=4)


#This is the latest player rankings using stratz data. Each player should have atleast 20 matches played to be included in the rankings
def generate_team_rankings_stratz(threshold=20):
    #get all matches in the league
    matches = load_all_matches_from_json(json_file_path="data/all_matches_stratz.json")
    #print(len(matches))

    #sort matches by id
    matches = sorted(matches, key=lambda x: x['match_id'])

    #dictionary of games recorded till now for each player
    player_game_count = {}

    #get all player ids
    players = load_all_players_dict_from_json_stratz()

    #ensure all players have mmr assigned, if not assign one
    for pid in players:    
        if players[pid]['mmr'] == 0:
            players[pid]['mmr'] = calculate_mmr_from_teams_played(pid)
            players[pid]['reliable_mmr'] = False
            #starting player game count
        #     players[pid]['match_count'] = -25#UNCLEARMMRPENALTY
        # else:
        #     players[pid]['match_count'] = 0  

        #starting player game count
        players[pid]['match_count'] = 0
        
        #store original mmr
        orig_mmr = players[pid]['mmr']
        players[pid]['stratz_mmr'] = orig_mmr

        
    
    #replay through all matches to update mmr
    count = 0
    for match in matches:
            count += 1
            # Find teams
            home_team_id = match['home_team_id']
            home_team_name = match['home_team']
            away_team_id = match['away_team_id']
            away_team_name = match['away_team']
            home_score = match['home_score']
            away_score = match['away_score']

            print(f"Match: {count} {home_team_name} vs {away_team_name} {home_score} - {away_score}")

            # Find players in teams
            ht_players = match['ht_players']
            at_players = match['at_players']

            print("Calculating average MMR for each team...")
            # Calculate average MMR for each team
            ht_avg_mmr = sum(players[player_id]['mmr'] for player_id in ht_players) / len(ht_players)
            at_avg_mmr = sum(players[player_id]['mmr'] for player_id in at_players) / len(at_players)
            print(f"Average MMR for {home_team_name}: {ht_avg_mmr}")
            print(f"Average MMR for {away_team_name}: {at_avg_mmr}")

            # MMR of all players before games
            print("Before:")
            print("=" * 40)
            print(f"Home Team: {home_team_name}")
            print("-" * 40)
            for pid in ht_players:
                print(f"{players[pid]['player_name']:<20} MMR: {players[pid]['mmr']}, Matches: {players[pid]['match_count']}")
            print("=" * 40)
            print(f"Away Team: {away_team_name}")
            print("-" * 40)
            for pid in at_players:
                print(f"{players[pid]['player_name']:<20} MMR: {players[pid]['mmr']}, Matches: {players[pid]['match_count']}")
            print("=" * 40)

            # Calculate match confidence
            all_players_match_counts = [players[pid]['match_count'] if players[pid]['match_count'] < MINMATCHES else MINMATCHES for pid in ht_players + at_players]
            match_confidence = round((sum(all_players_match_counts)/(len(all_players_match_counts)*MINMATCHES)),2)
            print(f"Match Confidence: {match_confidence}")

            # Update MMR for each player
            #home team players
            for pid in ht_players:
                score = home_score if home_score > away_score else 0
                players[pid]['mmr'] = round(calculate_elo_rating(players[pid]['mmr'], at_avg_mmr, score, players[pid]['match_count'], match_confidence),2)

                #update match count for player
                players[pid]['match_count'] += 1

            #away team players
            for pid in at_players:
                score = away_score if away_score > home_score else 0
                players[pid]['mmr'] = round(calculate_elo_rating(players[pid]['mmr'], ht_avg_mmr,score, players[pid]['match_count'],match_confidence),2)

                #update match count for player, cap at 50
                players[pid]['match_count'] += 1

           # MMR of all players after games
            print("After:")
            print("=" * 40)
            print(f"Home Team: {home_team_name}")
            print("-" * 40)
            for pid in ht_players:
                print(f"{players[pid]['player_name']:<20} MMR: {players[pid]['mmr']} Rank Confidence: {round((min(players[pid]['match_count']/MAXMATCHES,1)),2)}")
            print("=" * 40)
            print(f"Away Team: {away_team_name}")
            print("-" * 40)
            for pid in at_players:
                print(f"{players[pid]['player_name']:<20} MMR: {players[pid]['mmr']}", f"Rank Confidence: {round((min(players[pid]['match_count']/MAXMATCHES,1)),2)}")
            print("=" * 40)
    
    #filter out players with less than 10 matches played
    players = {pid: player for pid, player in players.items() if len(player['matches']) >= threshold}

    return players

if __name__ == "__main__":
    players = generate_team_rankings_stratz()

    #list all players from highest to lowest MMR
    #players = load_all_players_dict("data/all_players_updatedmmr.json")
    players = sorted(players.values(), key=lambda x: x['mmr'], reverse=True)
    

    player_rankings = []
    for player in players:
        # if player.team_mmr < 6000:
        #create new dictionary for rankings page
        player_ranking = {
            'pid': player['pid'],
            'player_name': player['player_name'],
            'mmr': player['mmr'],
            'player_teams': player['player_teams'],
            'matches': len(player['matches']),
            'reliable_mmr': player['reliable_mmr'],
            'stratz_mmr': player['stratz_mmr'],
            'rank_confidence': round((min(len(player['matches'])/MAXMATCHES,1.0)),2)
        }
        player_rankings.append(player_ranking)
    
    # Save updated player MMRs to CSV for visualization
    df = pd.DataFrame(player_rankings)
    df.to_csv('data/latest_player_rankings.csv', index=False, encoding='utf-8')
    #df.to_json('data/latest_player_rankings_kdynamic.csv')

    #save df to json
    with open('data/latest_player_rankings.json', 'w') as file:
        json.dump(player_rankings, file, indent=4)


    # # Display pandas DataFrame nicely
    # pd.set_option('display.max_columns', None)  # Show all columns
    # pd.set_option('display.max_rows', None)     # Show all rows
    # pd.set_option('display.width', 1000)        # Set display width
    # pd.set_option('display.colheader_justify', 'center')  # Center column headers
    # pd.set_option('display.precision', 2)       # Set precision for floating point numbers

    # print(tabulate(df, headers='keys', tablefmt='psql'))
    
    
    # # Save updated player MMRs to JSON
    # with open('data/all_players_updatedmmr_stratz.json', 'w') as file:
    #     json.dump(players, file, indent=4)
import requests
from tabulate import tabulate
import mysql.connector

def get_matches(player_id, num_matches=10):
    url = f"https://api.opendota.com/api/players/{player_id}/matches?limit={num_matches}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve matches: {response.status_code}")
        return []

def get_match_details_from_match(match_id):
    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve match details: {response.status_code}")
        return {}

def get_match_details_from_league(match_id, league_id):
    url = f"https://api.opendota.com/api/matches/{match_id}?league_id={league_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve match details: {response.status_code}")
        return {}

def get_league(league_id):
    url = f"https://api.opendota.com/api/leagues/{league_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve league: {response.status_code}")
        return {}

def get_matches_from_league(league_id):
    url = f"https://api.opendota.com/api/leagues/{league_id}/matches"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve matches: {response.status_code}")
        return []

def get_teams_from_league(league_id):
    url = f"https://api.opendota.com/api/leagues/{league_id}/teams"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve teams: {response.status_code}")
        return []



def query_db(query):
    try:
        # Connect to your MySQL DB
        conn = mysql.connector.connect(
            user="ad2l_reader",
            password="kS$^#sWI4!K^fNZt",
            host="charlie3.cprciz9jzrgp.us-east-1.rds.amazonaws.com",
            database="ad2l_production",
            port="3306",
            connection_timeout=10  # Set a timeout for the connection
        )

        # Open a cursor to perform database operations
        cur = conn.cursor(dictionary=True)

        # Execute a query
        cur.execute(query)

        # Retrieve query results
        results = cur.fetchall()

        # Close communication with the database
        cur.close()
        conn.close()

        return results

    except mysql.connector.Error as e:
        print(f"Operational error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():

    SEASON_IDS = "588, 589, 590, 591, 592, 593, 594"

    # query = f"""select ht.name 'Home Team', at.name 'Away Team', s.title 'Season', m.week 'Week', m.lobby_password 'Password', m.home_score 'Home Score', m.away_score 'Away Score' from matches m
    #                 inner join teams ht on m.home_participant_id = ht.id
    #                 inner join teams at on m.away_participant_id = at.id
    #                 inner join seasons s on m.season_id = s.id
    #                 where m.season_id in ({SEASON_IDS});
    #                 """
    
    query = """Select * from matches
                where (home_participant_id in (select id from teams where name = 'Slow Twitch Muscle Fibers')
                or away_participant_id in (select id from teams where name = 'Slow Twitch Muscle Fibers'))            
            ;"""
    
    result = query_db(query)
    #print(result)
    # if result:
    #     for row in result:
    #         # if row['Home Team'] == 'Slow Twitch Muscle Fibers' or row['Away Team'] == 'Slow Twitch Muscle Fibers':
    #         #     print(row)
    #         print(row)

    if result:
        print(tabulate(result, tablefmt="grid"))

if __name__ == "__main__":
    main()
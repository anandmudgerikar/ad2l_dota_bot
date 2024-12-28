import requests
from tabulate import tabulate
import mysql.connector
from config import stratz_token
import json
import tenacity
import time

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

def print_query_results(query):
    results = query_db(query)
    if results:
        print(tabulate(results, headers="keys", tablefmt="grid"))
    else:
        print("No results found.")

def query_stratz_iql(query, retries=5, wait=5):
    """
    Query the Stratz API using Graph QL.
    """
    
    url = "https://api.stratz.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "STRATZ_API",
        "Authorization": f"Bearer {stratz_token}"  # Replace with your actual access token
    }
    
    #special logic for stratz default token, #TODO: implement retry logic when switching to individual/multi tokens
    for wait_time in [1,2,60,61,60*60,(60*60)+10,60*60*24,10]:
        
        response = requests.post(url, json={'query': query}, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"Rate limited. waiting before repeating.")
            print(f"Waiting for {wait_time} seconds...")
            time.sleep(wait_time)    
        else:
            print(f"Query failed to run by returning code of {response.status_code}. {response.text}")
            return None
    
    print(f"Query failed after {retries} retries.")
    return None
        
def get_player_ranks_from_league_graph_query(player_id):
    """
    Get player info from a league using the Stratz API.
    """
    query = """
   {
    player(steamAccountId:%d)
    {
        ranks{
        rank,
        seasonRankId,
        asOfDateTime,
        isCore
        }
    }
    }
    """ % (player_id)

    return query_stratz_iql(query)

def get_matches_from_league_graph_query(league_id, step=100,end=700):
    """
    Get matches from a league using the Stratz API.
    """
    take = 100
    agg_response = []

    for skip in range(0,end,step):

        print(f"Getting matches from {skip} to {skip+step}...")
        response = _get_matches_from_league_graph_query(league_id, take, skip)
        #print(response)
        if response:
            #aggregate json responses
            agg_response.append(response)
    
    final_json = None
    for response in agg_response:
        if final_json:
            final_json['data']['league']['matches'] += response['data']['league']['matches']
        else:
            final_json = response        

    return final_json

def _get_matches_from_league_graph_query(league_id, take, skip):
    
    query = """
    {
      league(id: %d) {
        id
        name
        banner
        tier
        displayName
        matches(request: {take: %d, skip: %d}) {
          id
          didRadiantWin
          radiantTeam {
            id
            tag
            name
          }
          direTeam {
            id
            tag
            name
          }
          players {
            isRadiant
            steamAccount {
              name
              id
            }
            hero {
              displayName
            }
            kills
            goldPerMinute
            experiencePerMinute
            deaths
            assists
            numLastHits
          }
        }
      }
    }
    """ % (league_id, take, skip)

    return query_stratz_iql(query)

if __name__ == "__main__":

    pass
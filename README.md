Dota 2 Analysis Bot
Overview
This project aims to create a sophisticated bot for analyzing Dota 2 games. The bot's primary function is to provide insights on how to win a game of Dota 2 specifically for "YOU". Unlike generic language models that offer cookie-cutter advice, this bot strives to be objective and truthful by analyzing numerous replays of your games and those of your opponents.

Approach
To achieve this objective, we employ a crawl -> walk -> run approach:

Crawl: Teach the bot to analyze games from an amateur league and rank players based on their strength.
Walk: Enhance the bot's capabilities to analyze more complex game scenarios and provide deeper insights.
Run: Fully develop the bot to offer comprehensive game-winning strategies tailored to individual players.

Rankings Algorithm (CRAWL)
The initial phase focuses on ranking players in an amateur league. The main principles followed in the rankings algorithm are:

Data Collection: Gather data from various sources, including JSON and CSV files, containing player statistics and match details.
Player Initialization: Initialize player data, including MMR (Matchmaking Rating), team affiliations, and match history.
MMR Calculation: Calculate player MMR based on the highest level of the team they have played for and their performance in matches.
Filtering: Filter out players with less than a specified number of matches to ensure reliability.
Ranking: Rank players from highest to lowest MMR and calculate their rank confidence based on the number of matches played.
Files and Structure
rankings.py: Contains the main logic for generating player rankings.
data: Directory containing JSON and CSV files with player and match data.
utils.py: Utility functions for loading and processing data.
player.py: Defines the Player class and related functions.
team.py: Defines the Team class and related functions.
config.py: Configuration settings for the project.
constants.py: Constants used throughout the project.
data_loader.py: Functions for loading data from various sources.
db_utils.py: Utility functions for interacting with external databases and APIs.
test.py: Contains test functions for validating the bot's functionality.
Usage
To generate player rankings, run the rankings.py script:

This will process the data and save the updated player rankings to latest_player_rankings.csv and latest_player_rankings.json.

Future Work
Enhance the bot's analysis capabilities to provide deeper insights into game strategies.
Integrate more complex data sources and improve the accuracy of the rankings algorithm.
Develop a user interface for easier interaction with the bot.
Contributing
Contributions are welcome! Please feel free to submit issues and pull requests to improve the project.

License
This project is licensed under the MIT License. See the LICENSE file for details.
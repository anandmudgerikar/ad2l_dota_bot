# MMR Calculation Algorithm

## Overview
The MMR (Matchmaking Rating) calculation algorithm is designed to rank Dota 2 players based on their performance in matches. The algorithm uses an Elo rating system to update player MMRs after each match. Below are the detailed steps and principles of the algorithm.

## Core Principles
1. Wins and losses is all we care about. It doesn't matter how well you played or fed your brains out (maelk award), only if you won or lost. As they say, "It's all about the W.". This is the core principle of the Elo rating system. 
2. How much mmr you win or lose is based on the difference between your team's average mmr and the enemy team's average mmr.
3. If you havent played enough games, we don't trust you. The more untrustwrorthy players in a match, the less mmr is gained or lost.
4. But dont worry, once we have confidence in your rank, you can gain a lot of mmr in a single game. In a match with full confidence, you can gain or lose up to 60 mmr in a single game. We admit to having high recency bias as evident by the high ranks of all the current champions.
5. When the system is first initialized, we use your highest stratz mmr as the base mmr. This means that if you were immortal 1 at one point, but now you are legend 5, you will be initialized with the immortal 1 mmr. This is not ideal but we dont trust you so we assume you are still at your peak. As we record more games and the system grows more confident in your rank, the stratz mmr becomes less and less important and finally irrelevant. 

## Steps in the Algorithm

### 1. Data Loading
Load all match and player info from the AD2L database and using the stratz API. Note that only official AD2L matches from season 38 onwards are considered.

### 2. Player Initialization
Initialize every player with their base MMR from stratz. If a player has no stratz MMR, they are initialized with the average MMR of all teams they have played for. Our confidence in their rank is initialized to negative and they get flagged with "reliable_mmr=False" tag. This is likely due to your profile being private, so please make it public if you want to be ranked properly.

### 3. Match Processing
- Iterate through each match to update player MMRs.
- For each match:
  - Identify the home and away teams and their respective players.
  - Calculate the average MMR for both teams.

### 4. Match Confidence Calculation
- Calculate the match confidence based on the average confidence value of all players in the match. This is used to adjust the K value in the Elo rating formula.

### 5. MMR Update
- Update the MMR for each player based on the match outcome:
  - For home team players, update MMR if the home team wins or loses.
  - For away team players, update MMR if the away team wins or loses.

### 6. Filtering
- Filter out players with less than a specified number of matches (default is 20) to ensure reliability.

## Elo Rating Calculation
The Elo rating calculation is performed using the `calculate_elo_rating` function:
- **Inputs**:
  - `R_A`: Current rating of player A.
  - `R_B`: Current rating of player B (opponent).
  - `S_A`: Actual score of player A (1 for win, 0 for loss).
  - `player_game_count`: Number of games played by the player.
  - `match_confidence`: Confidence level of the match based on player match counts.
- **K Value Calculation**:
  - The K value is adjusted based on the match confidence.
- **Expected Scores**:
  - Calculate the expected scores for both players using the Elo formula.
- **New Ratings**:
  - Update the ratings for both players based on the actual score and expected score.

## Note
Some of the content in this project is AI-generated, so please review and use it carefully.
``` 

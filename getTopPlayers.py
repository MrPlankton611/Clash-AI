
import os
from dotenv import load_dotenv
import requests
import json
import time
 
load_dotenv()
CLASH_API_KEY = os.getenv("CLASH_API_KEY")
BASE_URL = os.getenv("BASE_URL")
top_clans = []
top_players = []
REQUEST_DELAY_SECONDS = 0.15  # Delay in seconds between requests
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {CLASH_API_KEY}"
}

 
# Read top clans and split comma-separated values into separate items

# Read top clans, split comma-separated values, and remove hashtags
with open("top_clans.csv", "r") as f:
    for line in f.read().splitlines():
        top_clans.extend([
            item.strip().replace('#', '')
            for item in line.split(",") if item.strip()
        ])

def get_top_players(clan_tag):
    url = f"{BASE_URL}/clans/%23{clan_tag}/members"
    time.sleep(REQUEST_DELAY_SECONDS)  # Respect API rate limits
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        data = data.get('items', [])
        # Extract player data
        return [item.get('tag') for item in data]
    else:
        print(f"Error fetching top players for clan {clan_tag}: {response.status_code} - {response.text}")
        return []
    


# Progress bar with color using ANSI escape codes
import sys

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█', color='\033[92m', reset='\033[0m'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = color + fill * filled_length + reset + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% ({iteration}/{total}) {suffix}', end='')
    if iteration == total:
        print()  # New line on complete

total_clans = len(top_clans)
for idx, i in enumerate(top_clans, 1):
    print_progress_bar(idx, total_clans, prefix='Progress', suffix=f'Clan: {i}', color='\033[93m')
    top_players.extend(get_top_players(i))

# Write top_players to a CSV file, removing hashtags
with open("top_players.csv", "w") as f:
    for player_tag in top_players:
        f.write(player_tag.replace('#', '') + "\n")
    
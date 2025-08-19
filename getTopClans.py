
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
CLASH_API_KEY = os.getenv("CLASH_API_KEY")
BASE_URL = os.getenv("BASE_URL")
TOP_CLAN_URL = "locations/global/rankings/clans"
top_clan_limit = 200
top_players = []
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {CLASH_API_KEY}"
}

def get_top_clans():
    url = f"{BASE_URL}/{TOP_CLAN_URL}?limit={top_clan_limit}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        data = data.get('items', [])
        return [item.get('tag') for item in data]
    else:
        print(f"Error fetching top clans: {response.status_code} - {response.text}")
        return []

top_clans = get_top_clans()
print("Top Clans:", top_clans)

with open("top_clans.csv", "w") as f:
    for clan_tag in top_clans:
        f.write(clan_tag + ",")
 
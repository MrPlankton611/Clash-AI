from bs4 import BeautifulSoup
import requests
import json
import os

url = "https://clashroyale.fandom.com/wiki/"

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
card_names = []
card_stats = ["cardType","isWinCondition","isCycleCard","isTank","isSpellBait","hasDeployEffect","spawnsUnits","isBuildingTargeter","hasCharge","isRanged","hitSpeed","firstHitSpeed","range","targets","unitCount","width","deployTime","movementSpeed"]
with open("clash_cards.json", "r") as f:
    data = json.load(f)
    card_names = [card["name"] for card in data.get("cards", [])]
    data = data.get("supportCards", [])
    card_names.extend([card["name"] for card in data])
    # Replace spaces with underscores for multi-word names
    card_names = [name.replace(" ", "_") for name in card_names]

def get_card_stats():
    for card in card_names:
        url = f"https://clashroyale.fandom.com/wiki/{card}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Fetching stats for card: {card}")
        tbody = soup.find_all('tbody')
        base_stats = tbody[0]
        base_stats = base_stats.find_all('tr')
        base_stats = base_stats[0].find_all('th')
        print(type(base_stats))
        stats = []
        for th in base_stats[1:-1]:
            
            strings = th.get_text(separator='\n', strip=True).split('\n')
            stats.extend(strings)
        print(stats)
        break
    

get_card_stats()
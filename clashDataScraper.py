from bs4 import BeautifulSoup
import requests
import json
import os

url = "https://clashroyale.fandom.com/wiki/"
#Remember that different rarities start at different levels
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
card_names = []
card_stats = ["cardType","isWinCondition","isCycleCard","isTank","isSpellBait","hasDeployEffect","spawnsUnits","isBuildingTargeter","hasCharge","isRanged","hitSpeed","firstHitSpeed","range","targets","unitCount","width","deployTime","movementSpeed"]
card_rarities = {
    "common": 1,
    "rare": 3,
    "epic": 6,
    "legendary": 9,
    "champion": 11,
}
with open("clash_cards.json", "r") as f:
    data = json.load(f)
    card_names = [card["name"] for card in data.get("cards", [])]
    data = data.get("supportCards", [])
    card_names.extend([card["name"] for card in data])
    # Replace spaces with underscores for multi-word names
    card_names = [name.replace(" ", "_") for name in card_names]


def get_card_rarity(name):
    name = name.lower()
    with open("clash_cards.json", "r") as f:
        data = json.load(f)
        for card in data.get("cards", []):
            if card["name"].lower() == name:
                return card.get("rarity", None)
        for card in data.get("supportCards", []):
            if card["name"].lower() == name:
                return card.get("rarity", None)
    return None

def get_card_base_stats():
    with open("clash_cards.json", "r") as f:
        data = json.load(f)

    def update_stats(card_obj, stats):
        card_obj["statsByLevel"] = {str(stat["level"]): {
            "hitpoints": stat["hitpoints"],
            "damage": stat["damage"],
            "dps": stat["dps"]
        } for stat in stats}

    for card_obj in data.get("cards", []):
        card = card_obj["name"].replace(" ", "_")
        card_space = card_obj["name"]
        print(f"Fetching base stats for card: {card}")
        url = f"https://clashroyale.fandom.com/wiki/{card}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        wiki_table = soup.findAll('table', {'class': 'wikitable'})
        if len(wiki_table) < 2:
            continue
        stats_table = wiki_table[1]
        rows = stats_table.find_all('tr')
        stats = []
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:
                level = cols[0].get_text(strip=True)
                hitpoints = cols[1].get_text(strip=True).replace(',', '')
                damage = cols[2].get_text(strip=True).replace(',', '')
                dps = cols[3].get_text(strip=True).replace(',', '')
                stats.append({
                    "level": int(level),
                    "hitpoints": int(hitpoints),
                    "damage": int(damage),
                    "dps": int(dps)
                })
        update_stats(card_obj, stats)

    for card_obj in data.get("supportCards", []):
        if "name" not in card_obj:
            continue
        card = card_obj["name"].replace(" ", "_")
        card_space = card_obj["name"]
        print(f"Fetching base stats for card: {card}")
        url = f"https://clashroyale.fandom.com/wiki/{card}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        wiki_table = soup.findAll('table', {'class': 'wikitable'})
        if len(wiki_table) < 2:
            continue
        stats_table = wiki_table[1]
        rows = stats_table.find_all('tr')
        stats = []
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:
                level = cols[0].get_text(strip=True)
                hitpoints = cols[1].get_text(strip=True).replace(',', '')
                damage = cols[2].get_text(strip=True).replace(',', '')
                dps = cols[3].get_text(strip=True).replace(',', '')
                stats.append({
                    "level": int(level),
                    "hitpoints": int(hitpoints),
                    "damage": int(damage),
                    "dps": int(dps)
                })
        update_stats(card_obj, stats)

    with open("clash_cards.json", "w") as f:
        json.dump(data, f, indent=2)

get_card_base_stats()

from bs4 import BeautifulSoup
import requests
import json
import os
import re
import time

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

SPELL_CARDS = {'Arrows', 'Lightning', 'Zap', 'Tornado', 'Giant_Snowball', 'Royal_Delivery', 'Earthquake', 'Fireball', 'Earthquake', 'Goblin_Barrel', 'Lightning', 'Freeze', 'Barbarian_Barrel', 'Poison', 'Goblin_Curse', 'Rage', 'Clone', 'Tornado', 'Void', 'Mirror', 'The_Log', 'Graveyard', 'Rocket'}
SPIRIT_CARDS = {'Fire_Spirit', 'Ice_Spirit', 'Electro_Spirit', 'Heal_Spirit'}
with open("clash_cards.json", "r") as f:
    data = json.load(f)
    card_names = [card["name"] for card in data.get("cards", [])]
    data = data.get("supportCards", [])
    card_names.extend([card["name"] for card in data])
    # Replace spaces with underscores for multi-word names
    card_names = [name.replace(" ", "_") for name in card_names]

def extract_number_in_parentheses(text):
    match = re.search(r'\((\d+)\)', text)
    return int(match.group(1)) if match else None

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


TEST_CARD = None  # Example: 'Knight'
#hi  
def get_card_base_stats():
    with open("clash_cards.json", "r") as f:
        data = json.load(f)
    
    def update_stats(card_obj, stats):
        card_obj["statsByLevel"] = {str(stat["level"]): {
            "hp": stat["hp"],
            "damage": stat["damage"],
            "dps": stat["dps"]
        } for stat in stats}
    
    for card_obj in data.get("cards", []):
        if TEST_CARD and card_obj["name"].lower() != TEST_CARD.lower():
            continue 
        card = card_obj["name"].replace(" ", "_")        
        card_space = card_obj["name"]        
        print(f"Fetching base stats for card: {card}")      
        url = f"https://clashroyale.fandom.com/wiki/{card}"        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        wiki_tables = soup.find_all('table', {'class': 'wikitable'})
        stats_table = None
        is_building = False
        stats = []        
        for table in wiki_tables:
            header_row = table.find('tr')
            if header_row:
                header_cols = header_row.find_all(['th', 'td'])
                if header_cols and header_cols[0].get_text(strip=True).lower() == 'level':
                    if len(header_cols) > 2 and "hitpoints lost per second" in header_cols[2].get_text(strip=True).lower() and card != "Elixir_Collector":
                        print("This is a building")
                        is_building = True
                        for row in table.find_all('tr')[1:]:
                            cells = row.find_all(['td'])
                            if len(cells) < 5:
                                continue
                            level = cells[0].get_text(strip=True).replace(',', '')
                            hitpoints = cells[1].get_text(strip=True).replace(',', '')
                            damage = cells[3].get_text(strip=True).replace(',', '')
                            dps = cells[4].get_text(strip=True).replace(',', '')
                            stats.append({
                                "level": int(level),
                                "hp": int(hitpoints),
                                "damage": int(damage),
                                "dps": int(dps)
                            })
                        update_stats(card_obj, stats)
                        with open("clash_cards.json", "w") as f:
                            json.dump(data, f, indent=2)
                        break  # Done with this card, go to next
                    else:
                        stats_table = table
                        break
        if is_building:
            continue
        if not stats_table:
            continue
        rows = stats_table.find_all('tr')
        stats = []
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4 and header_cols[3].get_text(strip=True) != 'Crown Tower Damage' and card not in SPELL_CARDS:
                if len(cols) >= 5 and header_cols[4].get_text(strip=True) == 'Healing Per Second':
                    level = cols[0].get_text(strip=True)
                    hitpoints = 0
                    damage = cols[1].get_text(strip=True).replace(',', '')
                    if 'x' in damage:
                        damage = extract_number_in_parentheses(damage)
                    dps = 0
                    stats.append({
                        "level": int(level),
                        "hp": int(hitpoints),
                        "damage": int(damage),
                        "dps": int(dps)
                    })
                    continue
                level = cols[0].get_text(strip=True)
                hitpoints = cols[1].get_text(strip=True).replace(',', '')
                damage = cols[2].get_text(strip=True).replace(',', '')
                dps = cols[3].get_text(strip=True).replace(',', '')
                if "x" in damage:
                    if card == "Electro_Dragon":
                        damage = damage[0:3]
                    else:  
                        damage = extract_number_in_parentheses(damage)
                if card == "Goblin_Demolisher":
                    damage = cols[4].get_text(strip=True).replace(',', '')
                    print(damage)
                stats.append({
                    "level": int(level),
                    "hp": int(hitpoints),
                    "damage": int(damage),
                    "dps": int(dps)
                })
                
            elif card in SPELL_CARDS:
                print("this is a spell")
                level = cols[0].get_text(strip=True)
                hitpoints = 0
                damage = cols[1].get_text(strip=True).replace(',', '')
                if 'x' in damage or 'X' in damage:
                    damage = extract_number_in_parentheses(damage)
                dps = 0
                stats.append({
                    "level": int(level),
                    "hp": int(hitpoints),
                    "damage": int(damage),
                    "dps": int(dps)
                })
            elif card in SPIRIT_CARDS:
                print("this is a spirit")
                level = cols[0].get_text(strip=True)
                hitpoints = cols[1].get_text(strip=True).replace(',', '')
                damage = cols[2].get_text(strip=True).replace(',', '')
                if 'x' in damage:
                    damage = damage[:2]
                dps = 0
                stats.append({
                    "level": int(level),
                    "hp": int(hitpoints),
                    "damage": int(damage),
                    "dps": int(dps)
                })
            elif card == "Wall_Breakers":
                print("this is a wall breaker")
                level = cols[0].get_text(strip=True)
                hitpoints = cols[1].get_text(strip=True).replace(',', '')
                damage = cols[2].get_text(strip=True).replace(',', '')
                if 'x' in damage:
                    damage = damage[:2]
                dps = 0
                stats.append({
                    "level": int(level),
                    "hp": int(hitpoints),
                    "damage": int(damage),
                    "dps": int(dps)
                })
            elif card == "Elixir_Collector":
                print("this is an elixir collector")
                level = cols[0].get_text(strip=True)
                hitpoints = cols[1].get_text(strip=True).replace(',', '')
                damage = 0
                dps = 0
                stats.append({
                    "level": int(level),
                    "hp": int(hitpoints),
                    "damage": int(damage),
                    "dps": int(dps)
                })
        update_stats(card_obj, stats)
        with open("clash_cards.json", "w") as f:
            json.dump(data, f, indent=2)

    # for card_obj in data.get("supportCards", []):
    #     if "name" not in card_obj:
    #         continue
    #     if TEST_CARD and card_obj["name"].lower() != TEST_CARD.lower():
    #         continue
    #     card = card_obj["name"].replace(" ", "_")
    #     card_space = card_obj["name"]
    #     print(f"Fetching base staasdfasssts for card: {card}")
    #     
    #     url = f"https://clashroyale.fandom.com/wiki/{card}"
    #     response = requests.get(url)
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     wiki_tables = soup.find_all('table', {'class': 'wikitable'})
    #     stats_table = None
    #     for table in wiki_tables:
    #         header_row = table.find('tr')
    #         if header_row:
    #             header_cols = header_row.find_all(['th', 'td'])
    #             if header_cols and header_cols[0].get_text(strip=True).lower() == 'level':
    #                 stats_table = table
    #                 break
    #     if not stats_table:
    #         continue
    #     rows = stats_table.find_all('tr')
    #     stats = []
    #     for row in rows[1:]:
    #         cols = row.find_all('td')
    #         if len(cols) >= 4:
    #             level = cols[0].get_text(strip=True)
    #             hitpoints = cols[1].get_text(strip=True).replace(',', '')
    #             damage = cols[2].get_text(strip=True).replace(',', '')
    #             dps = cols[3].get_text(strip=True).replace(',', '')
    #             stats.append({
    #                 "level": int(level),
    #                 "hp": int(hitpoints),
    #                 "damage": int(damage),
    #                 "dps": int(dps)
    #             })
    #     
    #     update_stats(card_obj, stats)
    # 
    # with open("clash_cards.json", "w") as f:
    #     
    #     json.dump(data, f, indent=2)
    # print("Finished")

get_card_base_stats()

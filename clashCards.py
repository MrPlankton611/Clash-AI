from dotenv import load_dotenv
import os
import requests
import json
import time

load_dotenv()
CLASH_API_KEY = os.getenv("CLASH_API_KEY")

BASE_URL = os.getenv("BASE_URL")

CARDS_URL = f"{BASE_URL}/cards"
REQUEST_DELAY_SECONDS = 0.15  # Delay in seconds between requests

SPELL_CARDS = {'Arrows', 'Fireball', 'Lightning', 'Zap', 'Tornado', 'Giant Snowball', 'Royal Delivery', 'Earthquake', 'Fireball', 'Earthquake', 'Goblin Barrel', 'Lightning', 'Freeze', 'Barbarian Barrel', 'Poison', 'Goblin Curse', 'Rage', 'Clone', 'Tornado', 'Void', 'Mirror', 'The Log', 'Graveyard','Rocket'}
print(len(SPELL_CARDS))
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {CLASH_API_KEY}"
}
def get_cards():
    response = requests.get(CARDS_URL, headers=headers)
    print(f"Card API request status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        data = data.get('items', [])
        cards_list = []
        for card in data:
            # Extract card name and id
            card_name = card.get('name')
            card_id = card.get('id')
            card_elixir_cost = card.get('elixirCost')
            card_rarity = card.get('rarity')
            card_max_evolution_level = card.get('maxEvolutionLevel') or 0
            card_has_evolution = card_max_evolution_level > 0
            # Add all requested fields, using defaults if not present
            card_obj = {
                "name": card_name,
                "id": card_id,
                "elixirCost": card_elixir_cost,
                "rarity": card_rarity,
                "maxEvolutionLevel": card_max_evolution_level,
                "hasEvolution": card_has_evolution,
                "EvolutionCycle": card.get('evolutionCycle', None),
                "statsByLevel": card.get('statsByLevel', {}),
                "cardType": card.get('cardType', None),
                "isWinCondition": card.get('isWinCondition', False),
                "isCycleCard": card.get('isCycleCard', False),
                "isTank": card.get('isTank', False),
                "isSpellBait": card.get('isSpellBait', False),
                "hasDeployEffect": card.get('hasDeployEffect', False),
                "spawnsUnits": card.get('spawnsUnits', False),
                "isBuildingTargeter": card.get('isBuildingTargeter', False),
                "hasCharge": card.get('hasCharge', False),
                "isRanged": card.get('isRanged', False),
                "hitSpeed": None,
                "firstHitSpeed": None,
                "range": None,
                "targets": None,
                "unitCount": None,
                "width": 0.0,
                "deployTime": None,
                "movementSpeed": None
            }
            # If statsByLevel is missing, add a default structure for levels 9-15
            if not card_obj["statsByLevel"]:
                card_obj["statsByLevel"] = {str(lvl): {
                    "hp": None,
                    "damage": None,
                    "dps": None,
                } for lvl in range(1, 16)}
            cards_list.append(card_obj)
        data1 = response.json()
        data1 = data1.get('supportItems', [])
        tower_cards = []
        for tower_troop in data1:
            tower_troop_name = tower_troop.get('name')
            tower_troop_id = tower_troop.get('id')
            tower_troop_rarity = tower_troop.get('rarity')
            # Add statsByLevel for tower troops (default structure for levels 9-15)
            stats_by_level = {str(lvl): {
                "hp": None,
                "damage": None,
                "dps": None,
            } for lvl in range(1, 16)}
            # Add all card fields for consistency
            tower_card_obj = {
                "name": tower_troop_name,
                "id": tower_troop_id,
                "elixirCost": None,
                "rarity": tower_troop_rarity,
                "maxEvolutionLevel": None,
                "hasEvolution": None,
                "EvolutionCycle": None,
                "statsByLevel": card.get('statsByLevel', stats_by_level),
                "cardType": "TowerTroop",
                "isWinCondition": None,
                "isCycleCard": None,
                "isTank": None,
                "isSpellBait": None,
                "hasDeployEffect": None,
                "spawnsUnits": None,
                "isBuildingTargeter": None,
                "hasCharge": None,
                "isRanged": True,
                "hitSpeed": None,
                "firstHitSpeed": None,
                "range": None,
                "targets": None,
                "unitCount": None,
                "width": 0.0,
                "deployTime": None,
                "movementSpeed": None
            }
            tower_cards.append(tower_card_obj)
        # Write both arrays to the JSON file as a single object
        output = {
            "cards": cards_list,
            "supportCards": tower_cards
        }
        with open("clash_cards.json", "w") as f:
            json.dump(output, f, indent=2)
        print(f"Wrote {len(cards_list)} cards and {len(tower_cards)} support cards to clash_cards.json")
    
    else:
        print(f"Error fetching cards: {response.status_code} - {response.text}")


get_cards()
print("Cards data fetched and saved successfully.")
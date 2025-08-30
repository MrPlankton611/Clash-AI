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

SPELL_CARDS = {'Arrows', 'Lightning', 'Zap', 'Tornado', 'Giant_Snowball', 'Royal_Delivery', 'Earthquake', 'Fireball', 'Earthquake', 'Goblin_Barrel', 'Lightning', 'Freeze', 'Barbarian_Barrel', 'Poison', 'Goblin_Curse', 'Rage', 'Clone', 'Tornado', 'Void', 'Mirror', 'The_Log', 'Graveyard', 'Rocket'}
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
            card_name = card.get('name')
            card_id = card.get('id')
            elixir_cost = card.get('elixirCost')
            rarity = card.get('rarity')
            max_evo = card.get('maxEvolutionLevel') or 0
            has_evo = max_evo > 0

            # Unified schema with defaults; Ollama/wikis will backfill many of these
            card_obj = {
                # Identity
                "id": card_id,
                "name": card_name,
                "type": card.get('cardType', None),  # troop|building|spell|champion (if provided)
                "rarity": rarity,
                "arenaUnlock": None,
                "hasEvolution": has_evo,
                "maxEvolutionLevel": max_evo,
                "isChampion": (card.get('cardType', '').lower() == 'champion'),

                # Cost & timings
                "elixirCost": elixir_cost,
                "deployTime": None,
                "firstHitDelay": None,
                "attackWarmup": None,
                "attackBackswing": None,
                "placement": None,

                # Movement & targeting
                "pathing": None,
                "targets": None,
                "targetingPriority": None,
                "retargetTime": None,
                "movementSpeed": None,
                "speedCategory": None,
                "canBypassTroops": None,

                # Attack model
                "damageType": None,
                "attackRangeMin": None,
                "attackRangeMax": None,
                "projectileSpeed": None,
                "splashRadius": None,
                "hitSpeed": None,
                "burstCount": None,
                "burstInterval": None,
                "knockback": None,
                "stunDuration": None,
                "slowPercent": None,
                "slowDuration": None,
                "resetsTarget": None,

                # Durations & penalties
                "lifetime": None,
                "spellDuration": None,
                "crownTowerDamagePenalty": None,
                "deathDamage": None,
                "deathSplashRadius": None,

                # Spawns
                "unitCount": None,
                "spawnOnDeploy": [],
                "spawnOnDeath": [],
                "periodicSpawn": None,

                # Strategy tags
                "isWinCondition": False,
                "isTank": False,
                "isMiniTank": False,
                "isSwarm": False,
                "isSplashDealer": False,
                "isAirDefender": False,
                "isBuildingTargeter": False,
                "isResetter": False,
                "isCycle": False,
                "isSiege": False,
                "isBridgeSpam": False,
                "isSpellBait": [],

                # Derived helpers
                "spellKillBreakpoints": {},
                "hpPerElixir": None,
                "dpsPerElixir": None,

                # Stats containers
                "statsByLevel": {},
                "normalizedAtTourney": None,
            }

            # Ensure statsByLevel has levels 1–15 structure ready
            if not card_obj["statsByLevel"]:
                card_obj["statsByLevel"] = {
                    str(lvl): {"hp": None, "damage": None, "dps": None}
                    for lvl in range(1, 16)
                }

            cards_list.append(card_obj)

        # Tower/support items
        data1 = response.json()
        support = data1.get('supportItems', [])
        tower_cards = []
        for si in support:
            stats_by_level = {
                str(lvl): {"hp": None, "damage": None, "dps": None}
                for lvl in range(1, 16)
            }
            tower_cards.append({
                "id": si.get('id'),
                "name": si.get('name'),
                "type": "towerTroop",
                "rarity": si.get('rarity'),
                "arenaUnlock": None,
                "hasEvolution": False,
                "maxEvolutionLevel": 0,
                "isChampion": False,

                "elixirCost": None,
                "deployTime": None,
                "firstHitDelay": None,
                "attackWarmup": None,
                "attackBackswing": None,
                "placement": None,

                "pathing": None,
                "targets": None,
                "targetingPriority": None,
                "retargetTime": None,
                "movementSpeed": None,
                "speedCategory": None,
                "canBypassTroops": None,

                "damageType": None,
                "attackRangeMin": None,
                "attackRangeMax": None,
                "projectileSpeed": None,
                "splashRadius": None,
                "hitSpeed": None,
                "burstCount": None,
                "burstInterval": None,
                "knockback": None,
                "stunDuration": None,
                "slowPercent": None,
                "slowDuration": None,
                "resetsTarget": None,

                "lifetime": None,
                "spellDuration": None,
                "crownTowerDamagePenalty": None,
                "deathDamage": None,
                "deathSplashRadius": None,

                "unitCount": None,
                "spawnOnDeploy": [],
                "spawnOnDeath": [],
                "periodicSpawn": None,

                "isWinCondition": False,
                "isTank": False,
                "isMiniTank": False,
                "isSwarm": False,
                "isSplashDealer": False,
                "isAirDefender": True,  # typical, can be refined later
                "isBuildingTargeter": False,
                "isResetter": False,
                "isCycle": False,
                "isSiege": False,
                "isBridgeSpam": False,
                "isSpellBait": [],

                "spellKillBreakpoints": {},
                "hpPerElixir": None,
                "dpsPerElixir": None,

                "statsByLevel": stats_by_level,
                "normalizedAtTourney": None,
            })

        output = {"cards": cards_list, "supportCards": tower_cards}
        with open("clash_cards.json", "w") as f:
            json.dump(output, f, indent=2)
        print(f"Wrote {len(cards_list)} cards and {len(tower_cards)} support cards to clash_cards.json")
    
    else:
        print(f"Error fetching cards: {response.status_code} - {response.text}")


get_cards()
print("Cards data fetched and saved successfully.")
import ollama
import requests
import bs4
import dotenv
import json
from bs4 import BeautifulSoup
import asyncio
from crawl4ai import *
card_names = []

try:
    with open("clash_cards.json", "r") as f:
        data = json.load(f)
        card_names = [card["name"] for card in data.get("cards", [])]
        data = data.get("supportCards", [])
        card_names.extend([card["name"] for card in data])
        card_names = [name.replace(" ", "_") for name in card_names]
except Exception as e:
    print(f"Error fetching card stats: {e}")
    

dotenv.load_dotenv()

URL = "https://clashroyale.fandom.com/wiki/"

async def main(card_name):
    
    async with AsyncWebCrawler() as crawl:
        result = await crawl.arun(
            url = URL + card_name,

        )
        page = result.markdown
       
        text = f"""
   You are a highly precise data extraction tool. Your task is to analyze the following text about a Clash Royale card and extract specific statistics.

    Return the output as a single JSON object. Do not include any other text, explanations, or code blocks outside of the JSON. If a stat is not found, use a null value.
    Use context clues of the website to extract stats that are not mentioned in the website.
    TEXT TO ANALYZE:
    ---
    {page}
    ---

    JSON SCHEMA TO FOLLOW:
    ```json
    {{
        "type": null, // e.g., "Troop", "Spell", "Building", only use one of those 3
        "deployTime": null, // Time in seconds for card to become active after placement ex:3.1
        "firstHitDelay": null, // Time in seconds from targeting to first attack ex: 12.1
        "placement": null, // e.g., "anywhere", "ownTerritory", only use those 2
        "targets": null, // What the card attacks, e.g., "ground", "air", "buildings", only use those 3
        "targetingPriority": null, // The order of targets, e.g., "buildings only", "highest HP", only use one of those 2
        "movementSpeed": null, // e.g., "Slow", "Medium", "Fast", only use one of those 3
        "canBypassTroops": null, // Whether a troop can ignore other units to hit a target
        "damageType": null, // e.g., "singleTarget", "areaDamage", "deathDamage", only use one of those 3
        "attackRangeMin": null, // Minimum attack range in tiles
        "attackRangeMax": null, // Maximum attack range in tiles
        "projectileSpeed": null, // Speed of a projectile in tiles/second
        "splashRadius": null, // Radius of a splash attack in tiles
        "hitSpeed": null, // Time in seconds between consecutive attacks
        "burstCount": null, // Number of hits in a single attack
        "burstInterval": null, // Time in seconds between hits in a burst
        "knockback": null, // The amount a unit pushes another back in tiles
        "stunDuration": null, // Time in seconds a unit is immobilized
        "slowPercent": null, // Percentage by which a unit's speed is reduced
        "slowDuration": null, // How long a slow effect lasts
        "resetsTarget": null, // Whether a card can reset a unit's target
        "lifetime": null, // Duration in seconds for buildings or spawned units
        "spellDuration": null, // Duration of a spell in seconds
        "crownTowerDamagePenalty": null, // Damage reduction percentage against crown towers
        "deathDamage": null, // Damage dealt when a unit is destroyed
        "deathSplashRadius": null, // Radius of death damage in tiles
        "unitCount": null, // Number of units spawned from a single card
        "spawnOnDeploy": [], // Units spawned on card deployment
        "spawnOnDeath": [], // Units spawned on unit death
        "periodicSpawn": null, // Units spawned periodically (e.g., spawners)
        "isWinCondition": false, // Whether the card is a primary way to take towers
        "isTank": false, // Whether the card is a high-HP unit used to absorb damage
        "isMiniTank": false, // A smaller, more defensive tank
        "isSwarm": false, // A card that spawns multiple low-HP units
        "isSplashDealer": false, // A card that deals area damage
        "isAirDefender": false, // A card primarily used to defend against air units
        "isBuildingTargeter": false, // A card that prioritizes buildings
        "isResetter": false, // A card that can reset an attack or charge
        "isCycle": false, // A low-elixir card used to cycle through the deck
        "isSiege": false, // A card that attacks from across the river
        "isBridgeSpam": false, // A deck archetype that pressures the bridge quickly
        "isSpellBait": [], // Cards used to bait opponent's spells, in list put spells that kills the card, or is a counter to it
        "spellKillBreakpoints": []// Spell damage vs. card HP breakpoints
        "hpPerElixir": null, // Calculated HP efficiency
        "dpsPerElixir": null // Calculated DPS efficiency
    }}
    """
                                  
        response = ollama.chat(
            model="mistral",
            messages=[
                {
                    'role': 'user',
                    'content': text
                }
            ]
        )
        print(response['message']['content']) 
if __name__ == "__main__":
    asyncio.run(main("Archers"))
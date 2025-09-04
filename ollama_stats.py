import ollama
import requests
import bs4
import dotenv
import json
from bs4 import BeautifulSoup

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

def get_card_obscure_stats(card_name):
    response = requests.get("https://clashroyale.fandom.com/wiki/{card_name}".format(card_name=card_name))
    
    # Get raw HTML
    raw_html = response.text
    
    # Save raw HTML to file
    html_filename = f"{card_name}_raw.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(raw_html)
    
    print(f"Raw HTML saved to {html_filename}")
    return raw_html

get_card_obscure_stats("Mega_Knight")
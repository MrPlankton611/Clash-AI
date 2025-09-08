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
       
        # Load prompt from file
        with open('prompt.txt', 'r') as f:
            prompt_template = f.read()
        
        # Replace placeholder with actual page content
        text = prompt_template.replace('{page_content}', page)
                                  
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
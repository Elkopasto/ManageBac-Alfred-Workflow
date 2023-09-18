import requests
import os
import sys
from bs4 import BeautifulSoup
import json

query = sys.argv[1]
cookie = os.environ['cookie']
cookies = {'Cookie': cookie}

json_data = None
link = ""

def fetch_grades(cards):
    items = []
    for card in cards[1:]:
        grades = card.find_all('div', class_='cell')
        title = grades[0].text
        subtitle = (grades[1].text)

        res = {
            "type": "file",
            "title": title.strip(),
            "subtitle": subtitle.strip(),
            "arg": url,
        }

        items.append(res)
    
    return json.dumps({"items": items}, indent=2)

with open("./resources/cache/classes.txt", "r") as f:
    json_data = json.load(f)
    for i in json_data["items"]:
        if i["title"] == query:
            link = i["arg"]

url = link + '/units'

try:
    page = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(page.text, 'html.parser')
except:
    print(json.dumps({"items": [{"type": "file", "title": "Seems like you're offline", "subtitle": "Mabyer try again later?"}]}))

sidebar = soup.find("div", class_="sidebar-items-list")
cards = sidebar.find_all('div', class_="list-item")
print(fetch_grades(cards))
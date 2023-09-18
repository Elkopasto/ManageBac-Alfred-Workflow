import requests
import os
import sys
from bs4 import BeautifulSoup
import json

# Recieve arguments
query = sys.argv[1]

# Retrieve cookies set in Alfred's environment variables
cookie = os.environ['cookie']
cookies = {'Cookie': cookie, 'Content-type': 'application/json'}

# Url dictionary which stores links to ManageBac sections
mb_url = "https://" + os.environ['school_domain'] + ".managebac.com" + "/student/"
url_dct = {"progress": mb_url + "ib/activity/cas",
            "notifications": mb_url + "notifications",
            "classes": mb_url + "classes/my",
            "grades": mb_url + "classes",
            "upcoming": mb_url + "tasks_and_deadlines",
            "timetables": mb_url + "timetables",
            "mb": mb_url}

def fetch_json(title, subtitle, arg, **kwargs):
    res = {
        "type": "file",
        "title": title,
        "subtitle": subtitle,
        "arg": arg
    }

    for key, value in kwargs.items():
        res[key] = value
    
    return res

def fetch_cas(cards):
    items = []

    for card in cards:
        title_holder = card.find("a", href = True)
        title = title_holder.text
        link = title_holder["href"]
        description = card.find("div", class_="text-ellipsis")
        description = description.text if description else "..."
        status = card.find(attrs={'data-title': True})["data-title"]

        res = fetch_json(title, description, mb_url + link + "/reflections", icon={"path": './resources/icons/' + status + '.png'},
                         mods={"cmd": {
                            "valid": True,
                            "arg": mb_url + link,
                            "subtitle": "Go to summary ➡️"
                        }})

        items.append(res)

    json_data = json.dumps({"items": items}, indent=2)
    with open("./resources/cache/progress.txt", "w+") as f:
        f.write(json_data)
    
    return json_data

def fetch_classes(cards):
    items = []

    for card in cards:
        title_holder = card.find("a", href = True)
        title = title_holder.text
        link = title_holder["href"]
        teacher = card.find(attrs={'title': True})["title"]

        res = fetch_json(title, teacher, mb_url + link[9:], mods = {"cmd": {
                    "valid": True,
                    "arg": title,
                    "subtitle": "Quick summary ➡️"
                }})

        items.append(res)

    json_data = json.dumps({"items": items}, indent=2)
    with open("./resources/cache/classes.txt", "w+") as f:
        f.write(json_data)
    
    return json_data

def fetch_upcoming(cards):
    items = []

    for card in cards:
        title_holder = card.find("a", href = True)
        title = title_holder.text
        link = title_holder["href"]

        month = card.find("div", class_="month").text
        day = card.find("div", class_="day").text
        
        res = fetch_json(title, month + " " + day, mb_url + link)

        items.append(res)

    json_data = json.dumps({"items": items}, indent=2)
    with open("./resources/cache/upcoming.txt", "w+") as f:
        f.write(json_data)
    
    return json_data

# Try requesting page contents
try:
    url = url_dct[query] 
    page = requests.get(url, cookies=cookies)
except: # Offline mode, which relies on cached data
    json_data = ""
    try:
        with open("./resources/cache/" + query + ".txt", "r") as f:
            json_data = json.load(f)
        print(json.dumps(json_data))
    except:
        print(json.dumps({"items": [{"type": "file", "title": "Seems like you're offline", "subtitle": "Mabyer try again later?"}]}))
        exit()

soup = BeautifulSoup(page.text, 'html.parser')

# Arguemnt switch
if (query == "progress"):
    # Parse HTML content
    cards = soup.find_all('div', class_="fusion-card-item fusion-card-item-collapse experience-section stretch activity-tile")
    print(fetch_cas(cards))
elif (query == "classes"):
    classes = soup.find_all('div', class_="fusion-card-item fusion-card-item-collapse ib-class-component")
    print(fetch_classes(classes))
elif (query == "upcoming"):
    tasks_holder = soup.find("div", class_="upcoming-tasks")
    cards = tasks_holder.find_all('div', class_="fusion-card-item short-assignment section flex flex-wrap")
    print(fetch_upcoming(cards))
elif (query == "timetables"):
    print(url_dct("timetables"))
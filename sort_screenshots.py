import requests
import json
import os
import time
import shutil
import re
import unicodedata
import time


def safe_filename(s):
    # Normalize the string (remove accents, symbols)
    #s = unicodedata.normalize('NFKD', s)
    #s = s.encode('ASCII', 'ignore').decode('ASCII')
    
    # Remove any non-alphanumeric character
    s = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', s)
    
    # Optionally, truncate the filename to 255 characters (common limit on many systems)
    s = s[:255]
    
    return s



def fallback_game_identify(id: str):
    #3.9KB for Forza Horizon 4 as opposed to 3.6MB for all steam game names
    fgi_url = f"https://store.steampowered.com/api/appdetails?appids={id}"
    response = requests.get(fgi_url)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Return App Name
        try:
            return data[id]["data"]["name"]
        except KeyError:
            return False
    else:
        print(f"Failed to fetch data from the API. Status code: {response.status_code}")
        data = None  # No valid data available

def find_game_name(id):
    game_name = False
    try:
        game_name = searchable_data[int(id)]["name"]
        print(f"Found {game_name}-{id} in JSON")
    except KeyError:
        try:
            game_name = GAMEID_CACHE[id]
            print(f"Found {game_name}-{id} in cached individual searches")
        except KeyError:
            game_name = fallback_game_identify(id)
            GAMEID_CACHE[id] = game_name
            print(f"Found {game_name}-{id} in individual search")
    
    return game_name

# Define constants
URL = 'https://api.steampowered.com/ISteamApps/GetApplist/v0001'
FILE_NAME = 'SteamAppList.json'
MAX_AGE = 72 * 60 * 60  # 72 hours in seconds
GAMEID_CACHE = {}
CWD = os.getcwd()

# Check if the file exists and is less than 24 hours old
if os.path.exists(FILE_NAME):
    file_age = time.time() - os.path.getmtime(FILE_NAME)
    if file_age < MAX_AGE:
        # Load data from the existing file
        with open(FILE_NAME, 'r', encoding='utf-8-sig') as file:
            data = json.load(file)
            print("Loaded data from JSON <72h old.")
    else:
        print("JSON is >72h old. Fetching data from API...")
        fetch_new = True
else:
    print("JSON does not exist. Fetching data from the API...")
    fetch_new = True

# Fetch data from the API if needed
if 'fetch_new' in locals():
    response = requests.get(URL)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Save the JSON data to a file
        with open(FILE_NAME, 'w', encoding='utf-8-sig') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"JSON saved to {FILE_NAME}.")
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        data = None  # No valid data available

# At this point, `data` contains the JSON data, whether loaded from a file or fetched from the API
if data:
    searchable_data = {app['appid']: {key: value for key, value in app.items() if key != 'appid'} for app in data['applist']['apps']['app']}
    #with open("a.test", "w", encoding="utf-8") as f: f.write(str(searchable_data))
    #print(json.dumps(data, indent=4))  # Pretty-print the JSON for debugging
    for filename in os.listdir(CWD):
        if filename.lower().endswith(".png"):
            game_id = filename[:-4].split("_", 1)[0]
            game_name = find_game_name(game_id)
            if game_name == False:
                print(f"Skipping {filename}, invalid ID")
                continue
            sanitised_game_name = safe_filename(game_name)
            if not os.path.exists(f"{CWD}/{sanitised_game_name}"):
                os.mkdir(f"{CWD}/{sanitised_game_name}")
                
            dest = f"{CWD}/{sanitised_game_name}/{filename}"
            add = 1
            #print(f"Checking for {CWD}/{sanitised_game_name}/{filename}")
            if os.path.exists(f"{CWD}/{sanitised_game_name}/{filename}"):
                print(f"Found duplicate filename at {dest}, generating new name")
                while True:
                    dest=f"{CWD}/{sanitised_game_name}/{filename[:-4]}_({add}).png"
                    if os.path.exists(dest):
                        add += 1
                    else:
                        break
            shutil.move(f"{CWD}/{filename}", dest)
            print(f"File saved as {dest}")
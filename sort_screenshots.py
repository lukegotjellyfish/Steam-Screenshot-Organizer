import requests
import json
import os
import time
import shutil
import re
import unicodedata
import time



# Define constants
API_KEY = "YOUR_STEAM_API_KEY_HERE"
URL = f'https://api.steampowered.com/IStoreService/GetAppList/v1/?key={API_KEY}&max_results=50000'
searchable_data = {}
FILE_NAME = 'SteamAppList.json'
MAX_AGE = 28 * 24 * 60 * 60  # Days, houors, minutes, seconds
MAX_AGE_STR = f"{MAX_AGE/24/60/60}d"
GAMEID_CACHE = {}
CWD = os.getcwd()


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
        game_name = searchable_data[id]
        #print(f"Found {game_name}-{id} in JSON")
    except KeyError:
        try:
            game_name = GAMEID_CACHE[id]
            #print(f"Found {game_name}-{id} in cached individual searches")
        except KeyError:
            game_name = fallback_game_identify(id)
            GAMEID_CACHE[id] = game_name
            #print(f"Found {game_name}-{id} in individual search")
    
    return game_name
    


# Check if the file exists and is less than 24 hours old
if os.path.exists(FILE_NAME):
    file_age = time.time() - os.path.getmtime(FILE_NAME)
    if file_age < MAX_AGE:
        # Load data from the existing file
        with open(FILE_NAME, 'r', encoding='utf-8-sig') as file:
            searchable_data = json.load(file)
            print(f"Loaded data from JSON <{MAX_AGE_STR} old.")
    else:
        print(f"JSON is >{MAX_AGE_STR} old. Fetching data from API...")
        fetch_new = True
else:
    print("JSON does not exist. Fetching data from the API...")
    fetch_new = True

# Fetch data from the API if needed
if 'fetch_new' in locals():
    
    LAST_APPID = 0
    while True:
        response = requests.get(URL+f"&last_appid={LAST_APPID}")

        if response.status_code == 200:
            # Parse the JSON response
            new_data = response.json()
            formatted_data = {}
            for item in new_data["response"]["apps"]:
                formatted_data[item["appid"]] = item["name"]
            #input(formatted_data)
            if searchable_data != {}:
                print(searchable_data)
                searchable_data.update(formatted_data)
            else:
                searchable_data = formatted_data
            #data.update(response.json())
            #print(data)
            try:
                LAST_APPID = new_data["response"]["last_appid"]
            except KeyError:
                # Found all games
                break
        else:
            print(f"Failed to fetch JSON. Status code: {response.status_code}")
            break

    # Save the JSON data to a file
    print(f"JSON saved to {FILE_NAME}.")
    with open(FILE_NAME, 'w', encoding='utf-8-sig') as file:
        json.dump(searchable_data, file, ensure_ascii=False, indent=4)


# At this point, `data` contains the JSON data, whether loaded from a file or fetched from the API
if searchable_data:
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
            print(f"File saved at {dest}")

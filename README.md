# Steam-Screenshot-Organizer
 [Requires a Steam API Key ](https://steamcommunity.com/dev/apikey)<br>
 Just external (PNG) screenshots for now. You could add external JPGs but I cba.<br>
 Extensive ChatGPT crap code

# How to use
Just whack sort_screenshots.py it into your extermal steam screenshots folder

>python sort_screenshots.py

Uses the current working directory (where you call python from)

The only file operation comand is shutil.move which uses copy2 by default which maintains metadata but use at your own peril, risk, and damnation.<BR>
I have added a check to avoid overwriting files with the same name, though this should only happen with exact duplicates when it comes to steam screenshots.

# Steam-Screenshot-Organizer
 Just external (PNGs) for now. 
 Extensive ChatGPT crap code

# How to use

>python sort_screenshots.py

Uses the current working directory (where you call python from)
<BR>Just whack it into your screenshots folder

The only file operation comand is shutil.move which uses copy2 by default which maintains metadata but use at your own peril, risk, and damnation.<BR>
I have added a check to avoid overwriting files with the same name, though this should only happen with exact duplicates when it comes to steam screenshots.

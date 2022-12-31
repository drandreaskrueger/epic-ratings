#!/usr/bin/env python3

##############################################
# settings.py
# 
#   if your 'failedDownloads' is not empty, 
#     you might want to add something here?
##############################################

# epicHistoryFile="PurchaseHistory_plaintext_20221226.txt"
epicHistoryFile="PurchaseHistory_plaintext.txt"

# you must provide ^ your own list of games, by visiting
# https://www.epicgames.com/account/transactions?productName=epicgames
# then press "SHOW MORE" until all your licenses are shown;
# then mark all, copy, and paste as plaintext into such a .txt file.

# lines before and after the table in that ^ file
contentStart = "Purchase History\n"
contentEnd="BACK TO TOP\n"

# main metacritic URL
metacriticUrl="https://www.metacritic.com/game"

# find all /pc/ games, or if not available then /ps4/, or if not, then /switch/
platformsOrdered = ["pc", "playstation-4", "switch"]

# for generating URLPATH automatically:
REMOVE_CHARS = (".", ":", "'", ",", '"')

REPLACERS = [
            (" - ","---"),
            (" ","-"),
            ("-ep-","-episode-")
            ]

# drop these sentences, e.g. for DLC to fall back to main game
REMOVE_SENTENCES=[
                    "A Post Nuclear Role Playing Game",
                    " - Enhanced Plus Edition",
                    ": Enhanced Edition",
                    "Year Two Season Three Epic Pack",
                    " - Carols, Candles and Candy",
                    " - Match Day",
                    " - Pearls From the East",
                    " - Standard Editio...",
                    ": Trials of Fear Edition",
                    " - Gold Edition",
                    " - Definitive Edition",
                    " and 1 more",
                    ]

# these could not be automatically transformed, so provide the URL path manually:
NAMES_MAPPER = {"Encased": "encased-a-sci-fi-post-apocalyptic-rpg",
                "PUBG: BATTLEGROUNDS" : "playerunknowns-battlegrounds",
                "Cave Story+" : "cave-story-+",
                'ARK Ragnarok' : "ark-survival-evolved---ragnarok-expansion",
                'ARK The Center' : "ark-survival-evolved---the-center-expansion",
                'Shadowrun Collection' : 'shadowrun-returns',
                'Commander Lilith DLC' : 'borderlands-2-commander-lilith-the-fight-for-sanctuary',
                'The Textorcist':'the-textorcist-the-story-of-ray-bibbia',
                'MudRunner' : 'spintires-mudrunner',
                'MudRunner - Ridge DLC' : 'spintires-mudrunner---the-ridge',
                'MudRunner - Valley DLC' : 'spintires-mudrunner---the-valley',
                'MudRunner - Old Timers DLC' : 'spintires-mudrunner---old-timers',
                'Crying Suns Demo' : 'crying-suns',
                'Halcyon 6' : 'halcyon-6-starbase-commander',
                'Godfall Challenger Edition' : 'godfall',
                'Cities: Skylines - Pearls From the East' : 'cities-skylines',
                'Geneforge 1 - Mutagen' : 'geneforge-1---mutagen',
                'Alba - A Wildlife Adventure' : 'alba-a-wildlife-adventure',
                'A Game Of Thrones: The Board Game Digital Edit...' : 'a-game-of-thrones-the-board-game---digital-edition',
                'Total War: WARHAMMER - Grombrindal The White D...' : 'total-war-warhammer---grombrindal-the-white-dwarf',
                'Borderlands: The Handsome Collection' : 'borderlands-2',
                'Rise of the Tomb Raider: 20 Year Celebration' : 'rise-of-the-tomb-raider',
                'Overcooked' : 'overcooked!'
                }

# these are not on metacritic (yet)
NAMES_IGNORER = ["PUBG Founder's Pack",
                 "Epic Cheerleader Pack",
                 'Cook, Serve, Delicious! 3?!',
                 'ARK Editor',
                 'ARK Crystal Isles',
                 'ARK Valguero',
                 'Ultra HD Texture Pack',
                 'Surviving Mars - Mysteries Resupply Pack',
                 'Total War: WARHAMMER - Assembly Kit',
                 ]

# headers needed, to avoid the 'TooManyRedirects: Exceeded 30 redirects'
# https://stackoverflow.com/a/42240682
headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}

# don't wait longer than this (raise the number if you have a bad internet connection)
TIMEOUT = 5

# store all HTML pages locally
downloadsFolder = "metacritic"

# in which order you want the resulting CSV:
COLUMN_ORDER=['game', 'metascore', 'metascoreBased', 'userscore', 'userscoreBased',
                'nops', 'released', 'platform', 'developer', 'publisher', 'genres']
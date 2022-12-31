# epic-ratings
Lookup (e.g. metacritic-) ratings for all (most of) my epicgames licenses. 

# quickstart

    python3 downloader.py
    python3 filesparser.py
    open metacritic/MyEpicGamesOnMetacritic-*.csv

1. Run with the included example file, to see what it does.
1. Read the `settings.py` to understand how the tweaking works.

# individualize
1. Use your own `PurchaseHistory_plaintext.txt` file.
1. Extend the exceptions in `settings.py` if needed (and possibly submit a pull-request to this repo)

# external packages

    pip3 install -r .\requirements.txt

    
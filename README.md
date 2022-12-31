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

    pip3 install -r requirements.txt

but better do all this in a [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv), to keep your host system unaffected.

# example result

![metacritic/example-table.png](metacritic/example-table.png)

Running 'quickstart' with the included `PurchaseHistory_plaintext.txt` example, the resulting CSV file can be sorted and formatted like this, e.g. with the free and opensource [LibreOffice Calc](https://www.libreoffice.org/discover/calc/). 
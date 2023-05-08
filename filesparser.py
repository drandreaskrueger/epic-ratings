#!/usr/bin/env python3

######################################################
#  filesparser.py  
#
#   since 31/12/2022
#     v02 31/12/2022
# 
#  takes all metacritic files from metacritic folder,
#     extracts metascore, userscore, and other infos, 
#      then stores all those results into a csv file,
#       for LibreOffice Calc, to sort by column, etc.
######################################################

import os, datetime, csv
from pprint import pprint
from bs4 import BeautifulSoup # pip3 install html5lib bs4 
from settings import downloadsFolder, platformsOrdered 
from settings import COLUMN_ORDER, EMPTY_COLUMNS


def myfiles(downloadsFolder, platformsOrdered):
    """
    simply read all files that begin with pc_, switch_, playstation-4_
    """
    filenames = sorted([name for name in os.listdir(downloadsFolder) 
                        if name.split("_")[0] in platformsOrdered])
    print ("Found %d files in folder '%s'." % (len(filenames), downloadsFolder))
    return filenames


def parseMetascore(soup, urlpath, resultsDict):
    """
    find the 'metascore' data in the page, by finding the relevant HTML tags
    """
    # metascore
    ms = soup.find('div', attrs = {'class':'score_summary metascore_summary'})
    metascoreFind = ms.find('span', attrs = {'itemprop':'ratingValue'})
    resultsDict["metascore"] = int(metascoreFind.text) if metascoreFind else 0

    # metascore number of reviews
    summary = ms.find('div', attrs = {'class' : 'summary'})
    criticReviews = summary.find('a', attrs = {'href':'%s/critic-reviews' % urlpath})
    resultsDict["metascoreBased"] = int(criticReviews.find('span').text.strip()) if criticReviews else 0


def parseUserscore(soup, urlpath, resultsDict):
    """
    find the 'userscore' data in the page, by finding the relevant HTML tags
    """
    # userscore
    us = soup.find('div', attrs = {'class':'userscore_wrap feature_userscore'})
    # print (us.prettify())
    userscoreTags = us.select("div[class^=metascore_w\ user\ large\ game]") # begins with operator
    if len(userscoreTags) !=1: # protect against a case that shouldn't happen anyway 
        raise Error("number of userscore tags not equal 1")#this threw undefined for me might want to look into it
    userscoreText = userscoreTags[0].text.strip()
    resultsDict["userscore"] = 0 if userscoreText=="tbd" else float(userscoreText)

    # userscore number of reviews
    usersummary = us.find('div', attrs = {'class' : 'summary'})
    userReviews = usersummary.find('a', attrs = {'href':'%s/user-reviews' % urlpath})
    answer=0
    if userReviews:
        answer = int(userReviews.text.replace("Ratings","").strip())
    else:
        # if there aren't enough ratings yet, 
        # they don't tell us how many there are, but how many are still missing
        um = usersummary.find('span', attrs = {'class':'connect4_msg'}).text.strip()
        answer = -int(um.replace("Awaiting","").replace("more rating","").replace("s",""))
    resultsDict["userscoreBased"] = answer


def parseOtherInfos(soup, resultsDict):
    """
    find other info in the page, by searching within the text body
    """
    # forget HTML, just parse the text
    textlines = [lines.strip() for lines in soup.body.text.split("\n") 
                    if lines.strip() != ""]
    #print("\n".join(textlines))
    
    # number of players
    try:
        nopsIndex = textlines.index("# of players:")
        nops = textlines[nopsIndex+1] if nopsIndex else ""
    except:
        nops = ""
    resultsDict["nops"]=nops

    # developer company & release date
    resultsDict["developer"] = textlines[textlines.index("Developer:")+1]
    resultsDict["released"] = textlines[textlines.index("Release Date:")+1]

    # genres are all in one line, but with many spaces inbetween    
    i = next(i for i,text in enumerate(textlines) if text.startswith("Genre(s):"))
    resultsDict["genres"] = textlines[i].replace("Genre(s):", "").replace(" ", "") # .split(",")

    i=textlines.index("Publisher:")
    j=textlines.index("Release Date:")
    resultsDict["publisher"] = "".join([line.strip() for line in textlines[i+1:j]])
    # print(i, j, resultsDict["publisher"])


def parseMetacriticFiles(filenames, downloadsFolder):
    """
    read all files, parse content on HTML tag level, and on text level
    """
    filename2results={}
    for i, name in enumerate(filenames): # [33:34]):
        platform, rest = name.split("_")
        game = rest.replace(".html", "")
        resultsDict={"platform" : platform, "game": game}
        urlpath = "/game/%s/%s" % (platform, game)
        print (i, platform, game, end =": ") # urlpath, end=" ")

        # read page file and turn into tag soup 
        with open(os.path.join(downloadsFolder, name), "r") as f:
            page = f.read()
        soup = BeautifulSoup(page, 'html5lib')
        # print(soup.prettify())

        # metascore
        parseMetascore(soup, urlpath, resultsDict)
        print ("ms={metascore:d} ({metascoreBased:d} revs)".format(**resultsDict), end="")

        # userscore
        resultsDict["userscore"], resultsDict["userscoreBased"] = 0, 0
        try: # there are faulty pages, with (tm) in the page URL, just ignore:
            parseUserscore(soup, urlpath, resultsDict)
        except:
            pass
        print ("; us={userscore:.1f} ({userscoreBased:d} revs)".format(**resultsDict), end="")

        # various other infos
        parseOtherInfos(soup, resultsDict)
        mystring="; released={released:s}; Dev={developer:s}; Publ={publisher:s}; Genres={genres:s}; #plyrs={nops:s}"
        print (mystring.format(**resultsDict))

        # append to results dict
        filename2results[game+"_"+platform] = resultsDict

    return filename2results


def compileGenres(filename2results):
    import csv

def compileGenres(filename2results):
    """
    Condense the list of 75 genres into 10 genregroups and return the counts of movies
    belonging to each genregroup as a new column in a new CSV file.
    """
    # Define the 10 genregroups and the genres that belong to each group
    genregroups = {
        "Action": ["Action", "Fighting", "Shooter", "Beat-'Em-Up", "Shoot-'Em-Up"],
        "Adventure": ["Adventure", "Metroidvania", "Open-World", "Platformer", "Point-and-Click"],
        "RPG": ["RPG", "ActionRPG", "PC-styleRPG"],
        "Simulation": ["Simulation", "CityBuilding", "Business/Tycoon", "Vehicle", "Train"],
        "Sports": ["Sports", "Basketball", "Soccer"],
        "Strategy": ["Strategy", "Tactical", "Tactics", "Real-Time", "Turn-Based"],
        "Casual": ["Puzzle", "Matching", "Pinball"],
        "Horror": ["Horror"],
        "MassivelyMultiplayer": ["MassivelyMultiplayer", "MassivelyMultiplayerOnline"],
        "Miscellaneous": ["Miscellaneous"]
    }
    
    # Initialize the genregroup counts to 0
    genregroup_counts = {genregroup: 0 for genregroup in genregroups}
    
    # Count the number of movies in each genregroup
    for fn, r in filename2results.items():
        for genre in r["genres"].split(","):
            genre = genre.strip()
            for genregroup, genres in genregroups.items():
                if genre in genres:
                    genregroup_counts[genregroup] += 1
                    break
    
    # Write the genregroup counts as a new column in a new CSV file
    with open("output.csv", "w", newline="") as csvfile:
        fieldnames = list(filename2results.values())[0].keys()
        fieldnames.append("Genregroup Counts")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for fn, r in filename2results.items():
            r["Genregroup Counts"] = ",".join(str(genregroup_counts[genregroup]) for genregroup in genregroups)
            writer.writerow(r)



def saveResults(filename2results, filename="MyEpicGamesOnMetacritic-%s.csv",
                columnOrder=COLUMN_ORDER, folder=downloadsFolder):
    """
    results into a timestamped csv file, and genres into a txt file
    """
    timestamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fn=os.path.join(folder, filename % timestamp)
    
    columns = columnOrder
    if not EMPTY_COLUMNS:
        columns = [c for c in columnOrder if c!='']

    with open(fn,"w", newline='') as f:
        csvwriter = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(columnOrder)
        for res in filename2results.values():
            row=[res.get(c,"") for c in columns]
            csvwriter.writerow(row)
    print("saved to:", fn)

    allGenres = compileGenres(filename2results)
    fn2 = fn.replace(".csv", "_genres.txt")
    with open(fn2,"w") as f:
        for genre in allGenres:
            f.write(genre+"\n")
    print("saved to:", fn2)


def main(downloadsFolder, platformsOrdered):
    filenames = myfiles(downloadsFolder, platformsOrdered)
    filename2results = parseMetacriticFiles(filenames, downloadsFolder)
    # pprint(filename2results)
    print("\nREADY.")
    allGenres = compileGenres(filename2results)
    print("#genres=%d:\n%s" % (len(allGenres), allGenres))
    saveResults(filename2results)
    

if __name__=="__main__":
    main(downloadsFolder, platformsOrdered)
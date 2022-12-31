#!/usr/bin/env python3

######################################################
# filesparser.py  
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

from settings import downloadsFolder, platformsOrdered, COLUMN_ORDER

def myfiles(downloadsFolder, platformsOrdered):
    """
    simply read all files that begin with pc_, switch_, playstation-4_
    """
    filenames = sorted([name for name in os.listdir(downloadsFolder) 
                        if name.split("_")[0] in platformsOrdered])
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
        raise Error("number of userscore tags not equal 1")
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
    """
    Had hoped to sort by single genre, but ~75 genres are a bit much.
    Idea for a TODO: Group these 75 genres into 7-10 genregroups, then
    create new table with 7-10 genregroups as titles, and Y/N columns.
    """
    allGenres=[]
    for fn,r in filename2results.items():
        genres = r["genres"].split(",")
        allGenres.extend(genres)
        # if "" in genres: print(fn) # these have unnecessary , in Genre(s)
    allGenres = sorted(list(set(allGenres))) # make unique
    if "" in allGenres:
        allGenres.remove("") # remove the empty genre
    return allGenres


def saveResults(filename2results, filename="MyEpicGamesOnMetacritic-%s.csv",
                columnOrder=COLUMN_ORDER, folder=downloadsFolder):
    """
    results into a timestamped csv file, and genres into a txt file
    """
    timestamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fn=os.path.join(folder, filename % timestamp)
    with open(fn,"w", newline='') as f:
        csvwriter = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(columnOrder)
        for res in filename2results.values():
            row=[res[c] for c in columnOrder]
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
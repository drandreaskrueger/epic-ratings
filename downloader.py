#!/usr/bin/env python3

##############################################
# downloader.py  
#
#   since 28/12/2022
#     v03 03/01/2023
# 
#   takes your PurchaseHistory_plaintext.txt,
#    creates metacritic URLs from game names,
#         and then downloads all those pages. 
##############################################

import sys
import os
import time
import csv
from pprint import pprint
import requests # pip3 install requests
from settings import * # do read that file, to adapt to your needs


def readEpicgamesPurchaseHistoryFile(epicHistoryFile,
                                        contentStart=contentStart,
                                        contentEnd=contentEnd):
    """
    read plaintext file, and extract the games table
    """
    with open(epicHistoryFile) as f:
        lines=f.readlines()
    # print(lines)
    start = lines.index(contentStart)
    end = lines.index(contentEnd) 
    print ("Done loading input file; relevant table is between lines %d and %d." % (start, end))
    myCsv=lines[start+1:end]
    return myCsv


def simplifyTitle(name, removeChars=REMOVE_CHARS, 
                        replacers = REPLACERS,
                        removeSentences=REMOVE_SENTENCES,
                        namesMapper=NAMES_MAPPER,
                        namesIgnorer=NAMES_IGNORER):

    """see comments in settings.py for how to adapt this"""

    # non automated = some games are just not there, on metacritic:
    if name in namesIgnorer:
        return False

    # non automated = manually assign urlpaths to game names:   
    if name in namesMapper:
        return namesMapper[name]    

    # semi automated = by dropping parts of the game names:
    for sentence in removeSentences:
        name = name.replace(sentence,"")

    # automated = rules based characters replacement, etc
    for rem in removeChars:
        name = name.replace(rem,"")

    name=name.lower()
    name=name.strip()

    for find, replace in replacers:
        name = name.replace(find,replace)

    return name


def createDownloadList(myCsv, debugging=False):
    """urlpath becomes the fifth column in the csv"""

    # print(myCsv)
    reader = csv.reader(myCsv, delimiter="\t")
    title = next(reader)
    title[4]="WEBSITEPATH"
    if debugging:
        print(title) 
        print()

    toDownload=[]
    for t in reader:
        if len(t)<2: # omit e.g. empty lines
            continue
        t[4]=simplifyTitle(t[1])
        if debugging:
            print(t)
        toDownload.append(t)
    
    print ("Done creating URLPATHs for most of those %d games." % len(toDownload))
    return toDownload


def makeFolderUnlessExists(foldername):
    if not os.path.exists(foldername):
        os.mkdir(foldername)


def DownloadPages(toDownload, printInfos=True, nice=NICENESS):
    """
        get all the pages:
        * make subfolder
        * skip over the excluded titles (not on metacritic yet)
        * check if downloaded already: first /pc/ then /playstation-4/ then /switch/
        * if not, then download page: pc, ps4, switch
        * possibly add to failedDownloads
        * or write to file
        after loop finishes:
        * show number of failedDownloads
        * return failedDownloads list
    """
    makeFolderUnlessExists(downloadsFolder)
    failedDownloads=[]

    # printer defined locally, changes behaviour via 'printInfos' variable
    def printInfo(text, end="\n", printInfos=printInfos):
        if printInfos:
            print(text, end=end)

    for i, game in enumerate(toDownload):
        printInfo ("%3d %10s %s" % (i, game[0], game[4]), end=" ")
        if game[4]==False:
            printInfo("IGNORE THIS TITLE '%s', IS PROBABLY NOT ON METACRITIC."%game[1])
            continue

        page = None
        for platform in platformsOrdered:
            filename=os.path.join(downloadsFolder, platform + "_" + game[4] + ".html")
            if os.path.exists(filename):
                printInfo ("ALREADY DOWNLOADED '%s' = skip." % platform)
                page = True
                break

        if page == True:
            continue

        for platform in platformsOrdered:
            printInfo (platform, end="")
            url = metacriticUrl + "/" + platform + "/" + game[4]
            # printInfo (url)

            try:
                page = requests.get(url=url, headers=headers, timeout=TIMEOUT)
            except:
                printInfo ("=failed, trying next:", end=" ")
            else:
                if page.status_code==200:
                    printInfo ("=succeeded, break.", end = " ")
                    print("..", end=""); sys.stdout.flush()
                    time.sleep(NICENESS)
                    print(".", end=" ")
                    break
                else:
                    printInfo("=failed with %s, trying next:" % page.status_code, end=" ")



        # printInfo(page)
        if page == None:
            failedDownloads.append(game)
            printInfo ("all=FAILED.")
        elif page.status_code!=200:
            failedDownloads.append(game + [page.status_code])
            printInfo ("all=FAILED.")
        else:
            filename=os.path.join(downloadsFolder, platform + "_" + game[4] + ".html")
            with open(filename, "w") as f:
                f.write(page.text)
            printInfo ("SUCCEEDED, PAGE SAVED.")

    print ("\nREADY. %d failed downloads." % len(failedDownloads))
    # pprint(failedDownloads)
    return failedDownloads


def failedDownloadsPrettyPrint(failedDownloads):
    pprint(["%s = %s = %s" % (t[5], t[4], t[1]) for t in failedDownloads])


def main(epicHistoryFile, printInfos):
    myCsv = readEpicgamesPurchaseHistoryFile(epicHistoryFile)
    toDownload = createDownloadList(myCsv)
    failedDownloads = DownloadPages(toDownload, printInfos=printInfos) # printInfos=False)
    failedDownloadsPrettyPrint(failedDownloads)


if __name__ == '__main__':
    main(epicHistoryFile=epicHistoryFile, printInfos=True)
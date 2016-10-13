#! /usr/bin/env python3

'''This program search for posts in Hacker News that have more
than numOfVotes votes in the newest 200 pages of HN and open
them in the browser when the user wants. The program preserve
the links on the hard disk to be opened when desired. The program
tries to prevent a link the user has seen from appearing to him again'''

import requests, bs4, webbrowser, sys, shelve, copy, time

# The url of the first page to be fetched
url = 'https://news.ycombinator.com/newest'
# Opening the file that contains the Dictionary variable which contains our links
linksFile = shelve.open('/usr/local/bin/pyHNOTLinks')
# When running the program for the first time, the linksFile
# will be empty so the 'except' statement will be executed
try:
    linksDict = linksFile['linksDict']
except:
    linksDict = {}
# This counter will count the number of links found in a single search
cntr = 1
# Ask the user how many pages to search in
numOfPages = int(input('# of pages = ?'))
# Ask the user what is the number of votes should a post have to save it
numOfVotes = int(input('# of votes = ?'))
# The search and saving of the links i
for i in range(numOfPages):
    # downloading the HTML page
    res = requests.get(url)
    # If an error occurs, raise an exception
    res.raise_for_status()
    print('Searching page' + str(i + 1) + '...')
    # pass the HTML code downloaded to the BeautifulSoup
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    # select the elements that has a CSS class named 'score'
    scores = soup.select('.score')
    for x in scores:
        # x = '100 points' for example
        y = x.text.split()[0]
        if int(y) > numOfVotes:
            # get the id of the post whose score meets the wanted criteria
            postId = x.get("id")
            # postId = 'score_12423' for example
            postId = postId.split('_')[1]
            # find the a element that contain the actual link. The a element
            # is found inside a tr element. We find the tr element using the id
            # we got previously
            postLinkElem = soup.select('tr[id={}] .storylink'.format(postId))
            # get the actual link from the a element
            postLink = postLinkElem[0].get('href')
            # check whether the link is already exist in the dictionary variable
            if postLink not in linksDict.keys():
                # the link is stored as a 'key' in the dictionary and the corresponding
                # 'value' is 0 or 1 followed by a the time when the link is added to the dictionary
                # 0 indicates that the link is not opened yet. 1 indicates the opposite
                linksDict[postLink] = '0_' + str(time.time())
                # Inform the user that a new link has been found
                print('>>>' + str(cntr) + ' - New link found <<<')
                cntr += 1
    # get the element that contains the link that leads to the previous page to continue the search
    moreLink = soup.select('.morelink')
    # we don't always find that link so we add the 'try except' statement
    try:
        # get the actual link and make it a valid address
        url = 'https://news.ycombinator.com/' + moreLink[0].get('href')
    except:
        # if no link found break the loop in order to prevent program crash
        break
# Tell the user how many links the dictionary contains
print('Links list contains now {} links'.format(len(linksDict)))
# Ask the user if he wish to open the links
answer = input('Do you want to open links now? [y/n]')
# if the user wants to open the links
if answer == 'y':
    print('Opening links...')
    # For each link the dictionary contains
    for link in linksDict.keys():
        # if the link has not been opened yet
        if linksDict[link].split('_')[0] == '0':
            # open the link
            webbrowser.open_new(link)
            # update the status of the link to reflect that the link has been opened
            linksDict[link] = '1'+linksDict[link][1:]
# if the user does not want to open the links
else:
    pass
# now we want to get rid of opened links that has been kept for more than
# 15 days in case the dictionary has 100 links or more
# Create a new dictionary
newLinksDict = {}
if len(linksDict) >= 100:
    # get the current time
    currentTime = float(time.time())
    # for each link in the dictionary
    for link in linksDict.keys():
        # get the time when the link has been added
        linkTime = float(linksDict[link].split('_')[1])
        # if the link has been added more than 15 days ago and has been opened,
        # do nothing; we don't want this link to be in the new dictionary
        if linkTime - currentTime > 1296000 and int(linksDict[link].split('_')[0]) == 1:
            pass
        # if we want to keep the link, add it to the new dictionary
        else:
            newLinksDict[link] = linksDict[link]
    # assign the new dictionary to the dictionary variable that holds our links
    linksDict = newLinksDict
# now save the dictionary variable that contains the
# links to a file in the hard disk for later use
linksFile['linksDict'] = copy.copy(linksDict)
linksFile.close()

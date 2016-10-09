#! /usr/bin/env python3

# This program search for posts in Hacker News that have more
# than numOfVotes votes in the newest 200 pages of HN and open
# them in the browser afterwards

import requests, bs4, webbrowser, sys, shelve, copy, time, pprint

url = 'https://news.ycombinator.com/newest'
linksFile = shelve.open('/usr/local/bin/pyHNOTLinks')
try:
    linksDict = linksFile['linksDict']
except:
    linksDict = {}
cntr = 1
print('# of pages = ?')
numOfPages = int(input())
print('# of votes = ?')
numOfVotes = int(input())
for i in range(numOfPages):
    res = requests.get(url)
    res.raise_for_status()
    print('Searching page' + str(i + 1) + '...')
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    scores = soup.select('.score')
    for x in scores:
        y = x.text.split()[0]
        if int(y) > numOfVotes:
            postId = x.get("id")
            postId = postId.split('_')[1]
            postLinkElem = soup.select('tr[id=%s] .storylink' % postId)
            postLink = postLinkElem[0].get('href')
            if postLink not in linksDict.keys():
                linksDict[postLink] = '0_' + str(time.time())
                print('>>>' + str(cntr) + ' - New link found <<<')
                cntr += 1
    moreLink = soup.select('.morelink')
    try:
        url = 'https://news.ycombinator.com/' + moreLink[0].get('href')
    except:
        break
print('Links list contains now {} links'.format(len(linksDict.keys())))
answer = input('Do you want to open links now? [y/n]')
if answer == 'y':
    print('Opening links...')
    for link in linksDict.keys():
        if linksDict[link].split('_')[0] == '0':
            webbrowser.open_new(link)
            linksDict[link] = '1'+linksDict[link][1:]
else:
    pass
newLinksDict = {}
if len(linksDict.keys()) >= 100:
    currentTime = float(time.time())
    for link in linksDict.keys():
        linkTime = float(linksDict[link].split('_')[1])
        if linkTime - currentTime > 1296000 and int(linksDict[link].split('_')[0]) == 1:
            pass
        else:
            newLinksDict[link] = linksDict[link]
    linksDict = newLinksDict
linksFile['linksDict'] = copy.copy(linksDict)

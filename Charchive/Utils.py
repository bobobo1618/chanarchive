#Author: Lucas Cooper
#Creation date: 01/06/2011
#Function: Retrieves a thread from 4chan and stores it in GridFS and
#          provides utility functions to other modules.
#Changelog: 

#20/06/2011: Added this comment block.
#20/06/2011: Migrated everything into modules for easier extension/interface.

import re, sys, gridfs
from pymongo import Connection
import lxml.html as html

if sys.version_info.major >= 3:
    import urllib.request as urllib
else:
    import urllib

#Returns the filename used for GridFS.
#Based on the 4chan /board/type/filename.ext
def fileNameFromUrl(url=None):
    filename = ''
    for x in url.strip().split('/')[-3:]:
        filename = filename+'/'+str(x)
    return filename

#Gets a 4chan thread using the number of workers specified by numWorkers.
def getThread(config, inurl=None, numWorkers=16):
    #The regular expression used to find images.
    
    #The s<num> on the end represents a stage.
    #Stage 1 is the original web page, stage 2 is the decoded file (a string)

    substitutions = [
        ('//images\.4chan\.org', '/image'),
        ('//[0-9]+\.thumbs.4chan.org', '/image')
    ]

    compiledSubstitutions = []
    for sub in substitutions:
        compiledSubstitutions.append((re.compile(sub[0]), sub[1]))

    db = Connection(config['dbUri'])[config['dbName']]
    fs = gridfs.GridFS(db)

    inpage = urllib.urlopen(inurl).read().decode(encoding='UTF-8', errors='ignore')
    
    filenames = []
    urls = []

    xdoc = html.fromstring(inpage)

    for a in xdoc.xpath('/html/body/form/div/div[@class="thread"]/div//a[@class="fileThumb"]'):
        url = urllib.urlunparse(urllib.urlparse(a.get('href'), 'http'))
        filenames.append(fileNameFromUrl(url))
        urls.append(url)
        url = urllib.urlunparse(urllib.urlparse(a.xpath('img/@src')[0], 'http'))
        filenames.append(fileNameFromUrl(url))
        urls.append(url)

    for url in urls:
        #Since getImage takes a tuple, a list of them is nice :)
        getImage((config, url, inurl))

    for sub in compiledSubstitutions:
        inpage = re.sub(sub[0], sub[1], inpage)
    
    #Stage 3 is the GridFS page.
    outpage = fs.get(fs.put(inpage, 
        filename = fileNameFromUrl(inurl), 
        encoding='utf8', 
        metadata={'threadurl':inurl, 'type':'thread', 'filenames':filenames}))
    return True

def getImage(intuple):
    config = intuple[0]
    db = Connection(config['dbUri'])[config['dbName']]
    fs = gridfs.GridFS(db)
    url = intuple[1]
    threadurl = intuple[2]
    #Puts the image in GridFS.
    fs.put(urllib.urlopen(url), 
        filename=fileNameFromUrl(url), 
        metadata={'imgurl':url, 'threadurl':threadurl, 'type':'image'})
    return True


import requests
from bs4 import BeautifulSoup


class Thread:
    def __init__(self, threadurl, threadhooks=[]):
        r = requests.get(threadurl)
        self.pagebody = r.text
        self.soup = BeautifulSoup(self.pagebody)
        self.threadurl = threadurl
        self.threadhooks = threadhooks
        self.processThread()

    def processThread(self):
        self.thread = {}
        self.thread['replies'] = []

        hThread = self.soup.find('div', {'class': 'thread'})
        self.thread['id'] = hThread.attrs['id'][1:]

        replies = hThread.findChildren(recursive=False)

        for reply in replies:
            thisReply = {}
            thisReply['id'] = reply.attrs['id'][2:]
            thisReply['text'] = reply.find('blockquote', {'class': 'postMessage'}).get_text('\n')
            thisReply['subject'] = reply.find('span', {'class': 'subject'}).text
            thisReply['time'] = reply.find('span', {'class': 'dateTime'}).attrs['data-utc']

            nameBlock = reply.find('span', {'class': 'nameBlock'})
            thisReply['posterName'] = nameBlock.find('span', {'class': 'name'}).text
            thisReply['posterID'] = nameBlock.find('span', {'class': 'posteruid'}).text

            try:
                thisReply['file'] = {}
                thisFile = reply.find('div', {'class': 'file'})
                fileText = thisFile.find('span', {'class': 'fileText'})
                thisReply['file']['url'] = fileText.find('a').attrs['href']
                thisReply['file']['filename'] = fileText.find('a').text
                thisReply['file']['originalName'] = fileText.find('span').attrs['title']

            except AttributeError:
                1

            self.thread['replies'].append(thisReply)

        for threadhook in self.threadhooks:
            threadhook(self.thread)

        return self.thread

import fourChan
from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError
import os
import requests
import mimetypes


class Thread(fourChan.Thread):
    def __init__(self, threadurl, process=True, threadhooks=[]):
        self.conn = S3Connection()
        self.bucketname = os.getenv('CHARCHIVE_S3_BUCKET_NAME', 'charchive')
        try:
            self.bucket = self.conn.get_bucket(self.bucketname)
        except S3ResponseError:
            self.bucket = self.conn.create_bucket(self.bucketname)

        threadhooks.append(self.S3Hook)
        fourChan.Thread.__init__(self, threadurl, process, threadhooks)

    def S3Hook(self, thread):
        for reply in thread['replies']:
            for repfile in reply['files']:
                url = repfile['url']
                if not url.startswith('http://') and url.startswith('//'):
                    url = 'http:' + url
                r = requests.get(url)
                newobject = self.bucket.new_key()
                mimetype = mimetypes.guess_type(url)[0]
                newobject.set_contents_from_string(r.content, {'Content-Type': mimetype})
                newobject.make_public()
                repfile['S3Url'] = 'http://' + self.bucketname + '.s3.amazonaws.com/' + newobject.name

    def processThread(self):
        fourChan.Thread.processThread(self)

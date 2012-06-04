#Author: Lucas Cooper
#Creation date: 20/06/2011
#Function: Runs a CherryPy server which serves the GridFS objects.
#Changelog:
 
#20/06/2011: Migrated everything into modules for easier extension/interface.

import cherrypy, gridfs, urllib
from pymongo import Connection
from mimetypes import guess_type
from mako.template import Template
from mako.lookup import TemplateLookup

from .Utils import getThread
from .Reassociate import reassociate
from .Order import orderFileLists

class Server:
    config = {
    'dbhost':'localhost',
    'dbPort':27017,
    'hostName':'127.0.0.1',
    'templateDir':'Templates',
    'cacheDir':'Cache',
    'cherryPyConf':'CherryPy.cfg',
    'dbName':'imagedb'}

    def __init__(self, newConfig={}):
        try: 
            for key in newConfig.keys():
                self.config[key] = newConfig[key]
        except:
            print('Argument must be a dictionary. Please read documentation.')
        self.templateLookup = TemplateLookup(directories=self.config['templateDir'], module_directory=self.config['cacheDir'])
        self.db = Connection(self.config['dbhost'], self.config['dbPort'])[self.config['dbName']]
        self.fs = gridfs.GridFS(self.db)
        self.col = self.db['fs.files']
        
    def start(self):
        cherrypy.quickstart(self, '/', self.config['cherryPyConf'])
        
    def index(self, args=None):
        return str(args)
    
    def getThread(self, board=None, path=None, id=None):
        try:
            getThread(self.config, 'http://boards.4chan.org/'+board+'/'+path+'/'+str(id))
        except:
            try:
                return(self.fs.get_version('/'+str(board)+'/'+path+'/'+str(id)))
            except:
                return("Well that was a miserable failure now wasn't it...")
        
    def thread(self, board=None, path=None, id=None):
        cherrypy.response.headers['Content-Type']='text/html'
        if id:
            try:
                return(self.fs.get_version('/'+str(board)+'/'+path+'/'+str(id)))
            except gridfs.errors.NoFile:
                try:
                    getThread(self.config, 'http://boards.4chan.org/'+board+'/'+path+'/'+str(id))
                except urllib.error.HTTPError:
                    return('404 on: '+'http://boards.4chan.org/'+board+'/'+path+'/'+str(id))
                    
                try:
                    return(self.fs.get_version('/'+str(board)+'/'+path+'/'+str(id)))
                except gridfs.errors.NoFile:
                    return('File not on server or 4chan')
        elif board:
            out = ''
            for filename in self.fs.list():
                try:
                    if filename.split('/')[1] == board:
                        meta = self.fs.get_version(filename).metadata
                        if meta['type'] == 'thread':
                            url = '/thread'+filename
                            out = out + '<p><a href="{0}">{1}</a></p>\n'.format(url, filename)
                except:
                    print('Derp')
            return(self.templateLookup.get_template('boring.tmpl').render(body=out, title="Thread List"))
        else:
            out = ''
            for filename in self.fs.list():
                meta = self.fs.get_version(filename).metadata
                try:
                    if meta['type'] == 'thread':
                        url = '/thread'+filename
                        out = out + '<p><a href="{0}">{1}</a></p>\n'.format(url, filename)
                except:
                    print('Derp')
            return(self.templateLookup.get_template('boring.tmpl').render(body=out, title="Thread List"))
                
    def image(self, board = 's', path = 'src', filename=None):
        cherrypy.response.headers['Content-Type']=guess_type(filename)[0]
        return self.fs.get_version('/'+board+'/'+path+'/'+filename)
    
    def gallery(self, board=None, path=None, id=None):
        out = ''
        if board and path and id:
            filename1 = '/'+board+'/'+path+'/'+id
            meta = self.fs.get_version(filename1).metadata
            for filename in meta['filenames']:
                meta2 = self.fs.get_version(filename).metadata
                if meta2['type'] == 'image':
                    url = '/image'+filename
                    out = out+'<img src="{0}" title="{1}" alt="{2}"/>\n'.format(url, filename.split('/')[-1].split('.')[0], meta2['threadurl'])
        else:
            for filename in self.fs.list():
                meta = self.fs.get_version(filename).metadata
                try:
                    if meta['type'] == 'image':
                        url = '/image'+filename
                        out = out+'<img src="{0}" title="{1}" alt="{2}"/>\n'.format(url, filename.split('/')[-1].split('.')[0], meta['threadurl'])
                except:
                    print('Derp')
        return(self.templateLookup.get_template('gallery.tmpl').render(images=out))
    def fixdb(self):
        reassociate()
        orderFileLists()
        return('Done')
    
    fixdb.exposed = True
    getThread.exposed = True
    gallery.exposed = True
    index.exposed = True
    image.exposed = True
    thread.exposed = True

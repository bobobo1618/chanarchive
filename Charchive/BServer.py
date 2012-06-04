import gridfs, urllib
import bottle
from bottle import route, mako_view as view, mako_template as template
from pymongo import Connection
from mimetypes import guess_type

from .Utils import getThread
from .Reassociate import reassociate
from .Order import orderFileLists

class BServer:

    config = {
        'dbHost':'localhost',
        'dbPort':27017,
        'dbName':'imagedb',
        'listenHost':'127.0.0.1',
        'listenPort': 8888,
        'templateDir':'Templates',
        'cacheDir':'Cache'
    }

    app = bottle.Bottle()

    def __init__(self, newConfig={}):
        try: 
            for key in newConfig.keys():
                self.config[key] = newConfig[key]
        except:
            print('Argument must be a dictionary. Please read documentation.')
        
        if self.config.get('templateDir'):
            bottle.TEMPLATE_PATH.append(self.config.get('templateDir'))

        self.db = Connection(self.config['dbHost'], self.config['dbPort'])[self.config['dbName']]
        self.fs = gridfs.GridFS(self.db)
        self.col = self.db['fs.files']

    def start(self):
        bottle.run(self.app, host=self.config['listenHost'], port=self.config['listenPort'])

    @app.route('/')
    def index():
        return template('boring.tmpl', title='App', body='<h1>Works!</h1>')
    
    @app.route('/getThread/<board>/<path>/<id>')
    def getThread(self, board=None, path=None, id=None):
        try:
            getThread(self.config, 'http://boards.4chan.org/'+board+'/'+path+'/'+str(id))
        except:
            try:
                return(self.fs.get_version('/'+str(board)+'/'+path+'/'+str(id)))
            except:
                return("Well that was a miserable failure now wasn't it...")
    
    @app.route('/thread/<board>/<path>/<id>')
    def thread(self, board=None, path=None, id=None):
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
            return(template('boring.tmpl', body=out, title="Thread List"))
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
            return(template('boring.tmpl', body=out, title="Thread List"))
    
    @app.route('/image/<board>/<path>/<filename>')
    def image(self, board = 's', path = 'src', filename=None):
        cherrypy.response.headers['Content-Type']=guess_type(filename)[0]
        return self.fs.get_version('/'+board+'/'+path+'/'+filename)
    
    @app.route('/gallery/<board>/<path>/<id>')
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
        return(template('gallery.tmpl', images=out))

    @app.route('/fixdb')
    def fixdb(self):
        reassociate()
        orderFileLists()
        return('Done')

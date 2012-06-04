import gridfs, bottle, os, sys
from bottle import route, mako_view as view, mako_template as template
from pymongo import Connection
from mimetypes import guess_type

from .Utils import getThread
from .Reassociate import reassociate
from .Order import orderFileLists

if sys.version_info.major >= 3:
    import urllib.request as urllib
else:
    import urllib

config = {
    'dbUri': os.environ.get('MONGOLAB_URI', 'mongodb://localhost:27017'),
    'dbName':'heroku_app1437419',
    'listenHost':'0.0.0.0',
    'listenPort': os.environ.get('PORT', 5000),
    'hostName': 'localhost',
    'templateDir':'Templates',
    'cacheDir':'Cache',
    'staticDir': '/home/lucas/Dev/Chanarchive/Static'
}

app = bottle.Bottle()

if config.get('templateDir'):
    bottle.TEMPLATE_PATH.append(config.get('templateDir'))

db = Connection(config['dbUri'])[config['dbName']]
fs = gridfs.GridFS(db)
col = db['fs.files']

def start():
    bottle.run(app, host=config['listenHost'], port=config['listenPort'])

@app.route('/static/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root=config['staticDir'])

@app.route('/')
def index():
    return template('boring.tmpl', title='App', body='<h1>Works!</h1>')

@app.route('/getThread/<board>/<path>/<id>')
def getThread_h(board=None, path=None, id=None):
    try:
        getThread(config, 'http://boards.4chan.org/'+board+'/'+path+'/'+str(id))
    except:
        try:
            return(fs.get_version('/'+str(board)+'/'+path+'/'+str(id)))
        except:
            return("Well that was a miserable failure now wasn't it...")

@app.route('/thread/<board>/<path>/<id>')
def thread(board=None, path=None, id=None):
    if id:
        try:
            return(fs.get_version('/'+str(board)+'/'+path+'/'+str(id)))
        except gridfs.errors.NoFile:
            try:
                getThread(config, 'http://boards.4chan.org/'+board+'/'+path+'/'+str(id))
            except urllib.HTTPError:
                return('404 on: '+'http://boards.4chan.org/'+board+'/'+path+'/'+str(id))

            try:
                return(fs.get_version('/'+str(board)+'/'+path+'/'+str(id)))
            except gridfs.errors.NoFile:
                return('File not on server or 4chan')
    elif board:
        out = ''
        for filename in fs.list():
            try:
                if filename.split('/')[1] == board:
                    meta = fs.get_version(filename).metadata
                    if meta['type'] == 'thread':
                        url = '/thread'+filename
                        out = out + '<p><a href="{0}">{1}</a></p>\n'.format(url, filename)
            except:
                print('Derp')
        return(template('boring.tmpl', body=out, title="Thread List"))
    else:
        out = ''
        for filename in fs.list():
            meta = fs.get_version(filename).metadata
            try:
                if meta['type'] == 'thread':
                    url = '/thread'+filename
                    out = out + '<p><a href="{0}">{1}</a></p>\n'.format(url, filename)
            except:
                print('Derp')
        return(template('boring.tmpl', body=out, title="Thread List"))

@app.route('/image/<board>/<path>/<filename>')
def image(board = 's', path = 'src', filename=None):
    bottle.response.headers['Content-Type'] = guess_type(filename)[0]
    return fs.get_version('/'+board+'/'+path+'/'+filename)

@app.route('/gallery/<board>/<path>/<id>')
def gallery(board=None, path=None, id=None):
    out = ''
    if board and path and id:
        filename1 = '/'+board+'/'+path+'/'+id
        meta = fs.get_version(filename1).metadata
        for filename in meta['filenames']:
            meta2 = fs.get_version(filename).metadata
            if meta2['type'] == 'image':
                url = '/image'+filename
                out = out+'<img src="{0}" title="{1}" alt="{2}"/>\n'.format(url, filename.split('/')[-1].split('.')[0], meta2['threadurl'])
    else:
        for filename in fs.list():
            meta = fs.get_version(filename).metadata
            try:
                if meta['type'] == 'image':
                    url = '/image'+filename
                    out = out+'<img src="{0}" title="{1}" alt="{2}"/>\n'.format(url, filename.split('/')[-1].split('.')[0], meta['threadurl'])
            except:
                print('Derp')
    return(template('gallery.tmpl', images=out))

@app.route('/fixdb')
def fixdb():
    reassociate()
    orderFileLists()
    return('Done')

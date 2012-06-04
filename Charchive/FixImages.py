from pymongo import Connection
import gridfs, sys, os, re
from .Utils import fileNameFromUrl

def fiximages():
    dbname = 'imagedb'
    db = Connection()[dbname]
    col = db['fs.files']
    fs = gridfs.GridFS(db)
    
    subre = re.compile(r'target=_blank\>\<img src=http://[0-9]\.thumbs\.4chan\.org/([a-zA-Z])*/thumb/.*\.(jpg|gif|png) ')
    subre1 = re.compile(r'<script(.|\n)*?>(.|\n)*?</script>')
    subre2 = re.compile(r'<link rel="alternate stylesheet".*>')
    subre3 = re.compile(r'title="Yotsuba">(.|\n)*<form name="delform"')
    subre4 = re.compile(r'<br clear=left><hr>(.|\n)*')
    for filename in fs.list():
        try:
            file1 = fs.get_version(filename)
            if file1.metadata['type'] == 'thread':
                meta = file1.metadata
                filestring = file1.read().decode()
                filestring = filestring.replace('</span><br><a href="http://images.4chan.org/', '</span><br><img src="/image/')
                filestring = re.sub(subre, '', filestring)
                filestring = filestring.replace('</a><blockquote>', '<blockquote>')
                filestring = filestring.replace('http://images.4chan.org/', '/image/')
                filestring = filestring.replace('http://static.4chan.org/css/yotsuba.9.css', '/static/yotsuba.css')
                filestring = re.sub(subre1, '', filestring)
                filestring = re.sub(subre2, '', filestring)
                filestring = re.sub(subre3, 'title="Yotsuba"><form name="delform"', filestring)
                filestring = re.sub(subre4, '</body></html>', filestring)
                filestring = filestring.replace('<link rel="shortcut icon" href="http://static.4chan.org/image/favicon.ico" />', '')
                filestring = filestring.replace('http://sys.4chan.org/b/imgboard.php', '')
                fs.put(filestring, filename=filename, encoding='utf8', metadata=meta)
        except:
            print('Derp')

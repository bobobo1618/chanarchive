from pymongo import Connection
import gridfs, sys, os, re

def killold():
    dbname = 'imagedb'
    db = Connection()[dbname]
    col = db['fs.files']
    fs = gridfs.GridFS(db)
    
    for filename in fs.list():
        if not filename == None:
            datedict = {}
            for x in col.find({'filename':filename}):
                datedict[x['_id']]=x['uploadDate']
            for fileid in sorted(datedict, key=datedict.get, reverse=True)[1:]:
                fs.delete(fileid)

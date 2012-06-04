from pymongo import Connection
import gridfs, sys, os
from .Utils import fileNameFromUrl

def orderFileLists():
    dbname = 'imagedb'
    db = Connection()[dbname]
    col = db['fs.files']
    fs = gridfs.GridFS(db)
    for filename in fs.list():
        file1 = fs.get_version(filename)
        try:
            if file1.metadata['type'] == 'thread':
                rawfile = col.find_one({'_id':file1._id})
                rawfile['metadata']['filenames'] = sorted(rawfile['metadata']['filenames'])
                col.save(rawfile)
        except:
            print('Error')

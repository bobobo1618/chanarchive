from pymongo import Connection
import gridfs, sys, os
from .Utils import fileNameFromUrl

def reassociate():
    dbname = 'imagedb'
    db = Connection()[dbname]
    col = db['fs.files']
    fs = gridfs.GridFS(db)
    
    for filename in fs.list():
        file1 = fs.get_version(filename)
        try:
            if file1.metadata['type'] == 'image':
                print(filename)
                threadurl = file1.metadata['threadurl']
                threadname = fileNameFromUrl(threadurl)
                thread = fs.get_version(threadname)
                threadnames = thread.metadata['filenames']
                try:
                    if threadnames.index(filename):
                        continue
                    else:
                        threadnames.append(filename)
                except:
                    threadnames.append(filename)
                rawthread = col.find_one({'_id':thread._id})
                rawthread['metadata']['filenames'] = threadnames
                col.save(rawthread)
        except TypeError:
            print()
        except gridfs.errors.NoFile:
            print('Nofile: '+filename)
                
if __name__ == '__main__':
    reassociate()

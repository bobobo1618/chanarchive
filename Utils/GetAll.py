#Author: Lucas Cooper
#Date: 01/06/2011
#Function: Gets and stores all files from GridFS in the specified directory.
#Changelog: Added this comment block.

from pymongo import Connection
import gridfs, sys, os

dbname = 'imagedb'

if __name__ == '__main__':
    db = Connection()[dbname]
    fs = gridfs.GridFS(db)
    
    for filename in fs.list():
        if not filename == None:
            try:
                outFile = open(os.path.abspath(sys.argv[-1]+'/'+filename), 'wb')
            except:
                os.system('mkdir -p '+str(os.path.abspath(sys.argv[-1])))
                outFile = open(os.path.abspath(sys.argv[-1]+'/'+filename), 'wb')
            outFile.write(fs.get_last_version(filename).read())
            outFile.close()
    

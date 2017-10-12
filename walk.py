#!/usr/bin/python -u
# encoding: utf8
import os
import sqlite3
from sets import Set
from colored import fg, bg, attr

db_file = 'fileIndex_sqlite.db'

if(os.path.isfile(db_file) == False):
    print "DB file doesn't exist, creating...\n"
    conn = sqlite3.connect(db_file)
    conn.execute('''CREATE TABLE fileIndex
           (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
           path           TEXT    NOT NULL,
           filename           TEXT    NOT NULL,
           size            INT     NOT NULL);''')

    print "Table created successfully\n";
else:
    conn = sqlite3.connect(db_file)
    print "Opened database successfully\n"



# Clean DB...
cursor = conn.execute("SELECT id, path, filename, size  from fileIndex")
for row in cursor:
    if (os.path.isfile(row[2])):
        # print "file exists: ", row[2]
        this_filesize = os.path.getsize(row[2])
        if (this_filesize != row[3]):
            print "Wrong file size (" + row[2] + ") stored: ", row[3]
            conn.execute("DELETE FROM fileIndex WHERE id='" + str(row[0]) + "'")
    else:
        print "file not exist: ", row[2]
        conn.execute("DELETE FROM fileIndex WHERE id='" + str(row[0]) + "'")
   # print "ID = ", row[0]
   # print "path = ", row[1]
   # print "filename = ", row[2]
   # print "size = ", row[3], "\n"
conn.commit()

print "\n\n"

#  Index files in current dir...
duplicates = Set() # save duplicates in set for later
runCount = 0
# Loop twice, first loop indexes, second time we can mark duplicates
while(runCount < 2):
    for dirpath, dirs, files in os.walk("."):
        path = dirpath.split('/')
        if(runCount == 1):
            print '|' + (len(path))*'---' + fg('dark_sea_green_4a') + '[',os.path.basename(dirpath),']' + attr('reset')
        for f in files:
            fileLineOutput = ''
            fileLineTreePadding = ''
            uniqueFlag = ''
            insertedFlag = ''
            duplicateFlag = ''
            duplicateCount = 0
            this_fullpath = dirpath + '/' + f
            this_filesize = os.path.getsize(this_fullpath)
            fileLineOutput = '|' + len(path)*'---' + f + ' ' + fg('blue') + str(this_filesize) + attr('reset')
            cursor = conn.execute("SELECT ID, path FROM fileIndex WHERE filename='" + f + "' AND size='" + str(this_filesize) + "'")
            result_length = len(cursor.fetchall())
            if(result_length == 0):
                conn.execute("INSERT INTO fileIndex (path, filename, size) VALUES('" + this_fullpath + "', '" + f + "', '" + str(this_filesize) + "')")
                insertedFlag = ' ' + fg('white') + bg('blue') + "Inserted: " + this_fullpath + attr('reset')
            else:
                cursor = conn.execute("SELECT ID, path FROM fileIndex WHERE filename='" + f + "' AND size='" + str(this_filesize) + "'")
                found_file_path = False
                for row in cursor:
                    if(row[1] == this_fullpath):
                        found_file_path = True
                    else:
                        duplicateCount += 1
                        if(runCount == 1):
                            duplicates.add(this_fullpath)
                if(found_file_path == False):
                    uniqueFlag = " Unique file:" + this_fullpath
                    conn.execute("INSERT INTO fileIndex (path, filename, size) VALUES('" + this_fullpath + "', '" + f + "', '" + str(this_filesize) + "')")
                    insertedFlag = ' ' + fg('white') + bg('green') + "Inserted: " + this_fullpath + attr('reset')
            if(duplicateCount > 0):
                duplicateFlag = ' ' + fg('white') + bg('red') + 'Duplicates found:' + str(duplicateCount) + attr('reset')
            if(runCount == 1):
                print fileLineOutput + uniqueFlag + insertedFlag + duplicateFlag

    conn.commit()
    runCount += 1
    pass

if( len(duplicates) > 0):
    print "\nDuplicates found:\n"
    for dup in duplicates:
        print dup

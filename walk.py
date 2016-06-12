import os
import sqlite3

sqliteFileName = 'test_sqlite.db';

if(os.path.isfile(sqliteFileName)):
	createTables = False;
else:
	createTables = True;
	print "Database not found, will be created:", sqliteFileName;

conn = sqlite3.connect('test_sqlite.db')
print "Opened database successfully"

if(createTables):
	conn.execute('''CREATE TABLE fileIndex
        (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
        path           TEXT    NOT NULL,
        filename           TEXT    NOT NULL,
        size            INT     NOT NULL);''')
	conn.commit();
	print "Table created successfully";

home = os.path.expanduser("~")
duplicateSpaceUsed = 0;
for dirpath, dirs, files in os.walk("."):	 
	path = dirpath.split('/')
	print '|', (len(path))*'---', '[',os.path.basename(dirpath),']'
	for f in files:
		this_fullpath = dirpath + '/' + f
		this_filesize = os.path.getsize(this_fullpath)
		#print '|', len(path)*'---', f, ' ', this_filesize
		cursor = conn.execute("SELECT ID, path FROM fileIndex WHERE filename=? AND size=?", (f, str(this_filesize)))
		result_length = len(cursor.fetchall())
		if(result_length == 0):
			conn.execute("INSERT INTO fileIndex (path, filename, size) VALUES(?, ?, ?)", (this_fullpath, f, str(this_filesize)))
			print "inserted: ", this_fullpath
		else:
			cursor = conn.execute("SELECT ID, path FROM fileIndex WHERE filename=? AND size=?", (f, str(this_filesize)))
			found_file_path = False
			for row in cursor:
				if(row[1] == this_fullpath):
					found_file_path = True
				else:
					print "Found Duplicate:", this_fullpath, " in:", row[1]
					duplicateSpaceUsed += this_filesize;
					print "duplicate Total=", duplicateSpaceUsed;
			if(found_file_path == False):
				print "Unique file:", this_fullpath
				conn.execute("INSERT INTO fileIndex (path, filename, size) VALUES(?, ?, ?)", (this_fullpath, f, str(this_filesize)))
				print "inserted: ", this_fullpath

conn.commit();
# cursor = conn.execute("SELECT id, path, filename, size  from fileIndex")
# for row in cursor:
#    print "ID = ", row[0]
#    print "path = ", row[1]
#    print "filename = ", row[2]
#    print "size = ", row[3], "\n"

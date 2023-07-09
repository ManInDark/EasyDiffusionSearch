import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

def get_1024x512_images():
    return cursor.execute("SELECT path FROM image WHERE width = '512' AND height = '1024'").fetchall()

for pv in get_1024x512_images():
    print(pv[0])
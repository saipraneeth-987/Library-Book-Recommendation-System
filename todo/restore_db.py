import csv
import sys
import sqlite3

# Connect to the SQLite database
#filepath = sys.argv[1]
filepath = "data/todos.csv"
connection = sqlite3.connect('data/todo.db')
cursor = connection.cursor()

cursor.execute("""drop table if exists items""")
cursor.execute("""
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description text,
    done BOOLEAN NOT NULL
)
""")

# Open the CSV file
with open(filepath, "r") as file:
    contents = csv.reader(file)

    # Skip the header row if it exists in the CSV
    next(contents, None)

    # Insert records into the 'todos' table
    insert_records = "INSERT INTO items (id, title, description, done) VALUES(?, ?, ?, ?)"
    cursor.executemany(insert_records, contents)

# Retrieve and display all rows to confirm data insertion
select_all = "SELECT * FROM items"
rows = cursor.execute(select_all).fetchall()
for r in rows:
    print(r)

# Commit changes and close the connection
connection.commit()
connection.close()

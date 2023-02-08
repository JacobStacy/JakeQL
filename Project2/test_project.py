import project
import sqlite3
import os

database = "test.db"
sql_file = "test.tables.01.sql"

result = ""
conn = project.connect(database)

with open(sql_file, 'r') as file:
    for line in file.readlines():
        result = conn.execute(line)
        

expected = ""
conn = sqlite3.connect(database)

with open(sql_file, 'r') as file:
    for line in file.readlines():
        expected = conn.execute(line)
    expected = expected.fetchall()
    

os.remove(database)

print("expected:",  expected)
print("student: ",  result)
print(str(expected) == str(result))
assert str(expected) == str(result)
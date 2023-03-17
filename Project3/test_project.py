import project
import sqlite3
import os

database = "test1.db"
sql_files = [
                # "test.delete.01.sql",
                # "test.delete.02.sql",
                # "test.distinct.01.sql",
                # "test.distinct.02.sql",
                # "test.ids.01.sql",
                # "test.ids.02.sql",
                # "test.ids.03.sql",
                # "test.ids.04.sql" ,
                # "test.ids.05.sql" ,
                # "test.insert-columns.01.sql",
                # "test.insert-columns.02.sql",
                # "test.insert-columns.03.sql",
                # # "test.join.01.sql",
                # # "test.join.02.sql",
                # # "test.join.03.sql",
                # "test.multi-insert.01.sql",
                # "test.multi-insert.02.sql",
                # "test.multi-insert.03.sql",
                "test.qualified.01.sql",
                # "test.qualified.02.sql",
                # "test.qualified.03.sql",
                # "test.regression.01.sql",
                # "test.regression.02.sql",
                # "test.update.01.sql",
                # "test.update.02.sql",
                # "test.update.03.sql",
                # "test.where.01.sql",
                # "test.where.02.sql",
                # "test.where.03.sql",
                # # "test.where.04.sql",
                # # "test.where.05.sql"
             ]

for sql_file in sql_files:
    print("FILE:", sql_file)
    try:
        os.remove(database)
    except:
        pass

    result = []
    conn = project.connect(database)

    with open(sql_file, 'r') as file:
        for line in file.readlines():
            result.append(conn.execute(line))
    conn.close()
            

    expected = []
    conn = sqlite3.connect(database)
    with open(sql_file, 'r') as file:
        for line in file.readlines():
            expected.append(conn.execute(line).fetchall())
    conn.close()

    


    print("expected:",  expected)
    print("student: ",  result)
    print(str(expected) == str(result))
    assert str(expected) == str(result)
    print("")
    
print("TOTAL: ", (len(sql_files) / 31) * 100, "%")
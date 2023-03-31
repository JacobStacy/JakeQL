import project
import sqlite3
import os
import subprocess

database = "test1.db"
sql_files = [
                # "test.connections.01.sql",
                "test.connections.02.sql",
                # "test.create_drop_table.01.sql",
                # "test.create_drop_table.02.sql",
                # "test.create_drop_table.03.sql",
                # "test.create_drop_table.04.sql",
                # "test.create_drop_table.05.sql",
                # "test.create_drop_table.06.sql",
                "test.isolation.01.sql",
                "test.isolation.02.sql",
                # "test.regression.01.sql",
                # "test.regression.02.sql",
                # "test.rollback.01.sql",
                # "test.rollback.02.sql",
                # "test.transaction_modes.01.sql",
                # "test.transaction_modes.02.sql",
                # "test.transaction_modes.03.sql",
                # "test.transaction.01.sql",
                # "test.transaction.02.sql",
                # "test.transaction.03.sql",
             ]

for sql_file in sql_files:
    print("FILE:", sql_file)
    try:
        os.remove(database)
    except:
        pass

    py_path = "C:/Users/Jacob Stacy/AppData/Local/Programs/Python/Python310/python.exe"
    cli_path = "e:/Work/Class/CSE-480/Project4/cli.py "

    proc = subprocess.Popen([py_path, cli_path,  f'{sql_file}'], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc.wait()
    result = proc.communicate()[0]
    
    
    proc2 = subprocess.Popen([py_path, cli_path,  f'{sql_file}', "--sqlite"], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc2.wait()
    expected = proc2.communicate()[0]
    
    


    
    print(str(expected) == str(result))
    if sql_file == "test.create_drop_table.02.sql" or sql_file == "test.create_drop_table.06.sql":
        assert expected.decode().splitlines()[-1] == result.decode().splitlines()[-1]
        print(expected.decode().splitlines()[-1] == result.decode().splitlines()[-1])
        
    elif (str(expected) != str(result) ):
        print("\n\nexpected:")
        print(*(expected.decode().splitlines()), sep='\n')
        print("\n\nstudent: ")
        print(*(result.decode().splitlines()), sep='\n')
        print('\n')
        assert str(expected) == str(result)
    
    print("")
    
print("TOTAL: ", (len(sql_files) / 20) * 100, "%")
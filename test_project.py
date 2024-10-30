import project
import sqlite3
import os
import sys
import subprocess

database = "test1.db"
sql_files = [
                "test.connections.01.sql",
                "test.connections.02.sql",
                "test.create_drop_table.01.sql",
                "test.create_drop_table.02.sql",
                "test.create_drop_table.03.sql",
                "test.create_drop_table.04.sql",
                "test.create_drop_table.05.sql",
                "test.create_drop_table.06.sql",
                "test.isolation.01.sql",
                "test.isolation.02.sql",
                "test.regression.01.sql",
                "test.regression.02.sql",
                "test.rollback.01.sql",
                "test.rollback.02.sql",
                "test.rollback.03.sql",
                "test.transaction_modes.01.sql",
                "test.transaction_modes.02.sql",
                "test.transaction_modes.03.sql",
                "test.transaction_modes.04.sql",
                "test.transactions.01.sql",
                "test.transactions.02.sql",
                "test.transactions.03.sql",
                "test.transactions.04.sql",
                "test.transactions.05.sql",
                "test.delete.01.sql",
                "test.delete.02.sql",
                "test.distinct.01.sql",
                "test.distinct.02.sql",
                "test.ids.01.sql",
                "test.ids.02.sql",
                "test.ids.03.sql",
                "test.ids.04.sql" ,
                "test.ids.05.sql" ,
                "test.insert-columns.01.sql",
                "test.insert-columns.02.sql",
                "test.insert-columns.03.sql",
                "test.join.01.sql",
                "test.join.02.sql",
                "test.join.03.sql",
                "test.multi-insert.01.sql",
                "test.multi-insert.02.sql",
                "test.multi-insert.03.sql",
                "test.qualified.01.sql",
                "test.qualified.02.sql",
                "test.qualified.03.sql",
                "test.regression.01.sql",
                "test.regression.02.sql",
                "test.update.01.sql",
                "test.update.02.sql",
                "test.update.03.sql",
                "test.where.01.sql",
                "test.where.02.sql",
                "test.where.03.sql",
                "test.where.04.sql",
                "test.where.05.sql",
                "test.aggregate.01.sql",
                "test.aggregate.02.sql",
                "test.aggregate.03.sql",
                "test.default.01.sql",
                "test.default.02.sql",
                "test.desc.01.sql",
                "test.desc.02.sql",
                "test.parameters.01.sql",
                "test.parameters.02.sql",
                "test.view.01.sql",
                "test.view.02.sql",
                "test.view.03.sql",
                "test.view.04.sql",
                "test.view.05.sql",
                "test.view.06.sql",
                "test.view.07.sql",
                "test.view.08.sql",
             ]

error_tests = [
    "test.create_drop_table.02.sql",
    "test.create_drop_table.06.sql",
    "test.isolation.02.sql",
    "test.transaction_modes.02.sql",
    "test.transaction_modes.03.sql",
    "test.transactions.04.sql",
    "test.transactions.05.sql",
    "test.rollback.03.sql",
]

for sql_file in sql_files:
    print("FILE:", sql_file)
    try:
        os.remove(database)
    except:
        pass

    sql_file = "/sql_files/" + sql_file
    # Use sys.executable to get the current Python interpreter's path
    py_path = sys.executable
    cli_path = "cli.py"
    
    print(py_path)
    
    
    proc2 = subprocess.Popen([py_path, cli_path,  f'{sql_file}', "--sqlite"], shell = False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc2.wait()
    expected = proc2.communicate()[0]

    proc = subprocess.Popen([py_path, cli_path,  f'{sql_file}'], shell = False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc.wait()
    result = proc.communicate()[0]
      
    print(str(expected) == str(result))
    if sql_file in error_tests:
        print("\n\n\n\n\n ERRROR TEST:  #################")
        print("\nexpected:")
        print(*(expected.decode().splitlines()), sep='\n')
        print("\n\nJakeQL: ")
        print(*(result.decode().splitlines()), sep='\n')
        print('\n')
        assert expected.decode().splitlines()[-1] == result.decode().splitlines()[-1]
        print(expected.decode().splitlines()[-1] == result.decode().splitlines()[-1])
        print("#################\n\n\n")
        
    elif (str(expected) != str(result) ):
        print("\n\nexpected:")
        print(*(expected.decode().splitlines()), sep='\n')
        print("\n\nJakeQL: ")
        print(*(result.decode().splitlines()), sep='\n')
        print('\n')
        assert str(expected) == str(result)
    
    print("")
    
print("TOTAL: ", (len(sql_files) / (24 + 31 + 15)) * 100, "%")
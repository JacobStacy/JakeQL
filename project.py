import string
import operator

from copy import deepcopy
from bisect import insort

_ALL_DATABASES = {}
SHARED = 0
RESERVED = 1
EXCLUSIVE = 2

number_of_connections = 0


class Tokenizer():
    def collect_characters(self, query, allowed_characters):
        letters = []
        for letter in query:
            if letter not in allowed_characters:
                break
            letters.append(letter)
        return "".join(letters)


    def remove_leading_whitespace(self, query, tokens=None):
        whitespace = self.collect_characters(query, string.whitespace)
        return query[len(whitespace):]


    def remove_word(self, query, tokens):
        word = self.collect_characters(query, string.ascii_letters + '_' + '.' + '*' + string.digits)
        
        if word == "IS":
            if query[len(word):len(word) + 4] == " NOT":
                word += " NOT"
        
        if word == "NULL":
            tokens.append(None)
        else:
            tokens.append(word)
        return query[len(word):]


    def remove_text(self, query, tokens):
        assert query[0] == "'"
        query = query[1:]
        
        text = []
        while 1:
            if query[0] == "'":
                query = query[1:]
                if len(query) > 0 and query[0] == "'":
                    text.append(query[0])
                    query = query[1:]
                    continue
                break
            
            text.append(query[0])
            query = query[1:]
            
        tokens.append("".join(text))
        return query

    def remove_number(self, query, tokens):
        assert query[0] in string.digits
        
        # Grab all digits to the end or to a '.'
        num1 = self.collect_characters(query, string.digits)
        query = query[len(num1):]
        
        # Check if float 
        if query[0] != '.':
            tokens.append(int(num1)) # Add int
        else:
            
            # Collect and remove after '.'
            num2 = self.collect_characters(query, string.digits + '.')
            query = query[len(num2):]
            
            tokens.append(float(num1 + num2)) # Add float
        
        return query


    def tokenize(self, query):
        tokens = []
        while query:
            # print("Query:{}".format(query))
            # print("Tokens: ", tokens)
            old_query = query

            # Handle whitespace
            if query[0] in string.whitespace:
                query = self.remove_leading_whitespace(query, tokens)
                continue

            # Handle keywords
            if query[0] in (string.ascii_letters + '_'):
                query = self.remove_word(query, tokens)
                continue

            # Handle misc char
            if query[0] in "(),;*!=><?":
                if query[0] == '!' and query[1] == "=":
                    tokens.append(query[0:2])
                    query = query[2:]
                else:
                    tokens.append(query[0])
                    query = query[1:]
                continue

            # Handle text
            if query[0] in "'":
                query = self.remove_text(query, tokens)
                continue
            
            # Handle numbers
            if query[0] in string.digits:
                query = self.remove_number(query, tokens)
                continue

            if len(query) == len(old_query):
                raise AssertionError("Query didn't get shorter.")

        return tokens
    
class Lock:
    
    def __init__(self, conn_number, level):
        self.level = level
        self.conn_number = conn_number
        self.committed = False
        
    def __str__(self):
        return f"Conn:{self.conn_number} Lvl:{self.level} Commit: {self.committed}"
    
    def __repr__(self):
        return f"Conn:{self.conn_number} Lvl:{self.level} Commit: {self.committed}"
        
    def __eq__(self, b):
        return self.level == b
    
    def __lt__(self, b):
        return self.level < b
    
    def __gt__(self, b):
        return self.level > b

class Connection:
    
    
    def __init__(self, filename):
        if filename not in _ALL_DATABASES:
            _ALL_DATABASES[filename] = Database(filename)
        
        self.real_name = filename
        _ALL_DATABASES[filename].real = _ALL_DATABASES[filename]
        self.database = None
        self.working_database = None
        self.locks_held = []
        self.in_transaction = False
        
        global number_of_connections
        self.conn_number = number_of_connections
        number_of_connections += 1

        # Transaction modes, 0 = DEFFERED, 1 = IMMEDIATE, 2 = EXCLUSIVE
        self.transaction_mode = 0
        
    def add_lock(self, lock_level):
        self.database.real.locks = _ALL_DATABASES[self.real_name].locks
        self.locks_held.append(self.database.set_lock(self.conn_number, lock_level))            
                
    def __start_transaction(self):    
        self.working_database = deepcopy(_ALL_DATABASES[self.real_name])
        
    def __commit(self):
        for i in range(len(self.locks_held)): 
            self.locks_held[i].committed = True
        
        self.locks_held = []
        
        if self.working_database is not None:
            _ALL_DATABASES[self.real_name] = deepcopy(self.working_database)
        self.working_database = None
        self.transaction_mode = 0
        
    def __rollback(self):
        self.working_database = None
        for i in range(len(self.locks_held)): 
            self.locks_held[i].committed = True
        self.transaction_mode = 0
        
    def executemany(self, statement, values):
        for value_set in values:
            self.execute(statement, value_set)
            
    def execute(self, statement, parameters=[], tokens=[]):
        """
        Takes a SQL statement.
        Returns a list of tuples (empty unless select statement
        with rows to return).
        """
        if len(tokens) == 0:
            tokens = Tokenizer().tokenize(statement)
            params = parameters
            for i in range(len(tokens)):
                if tokens[i] == '?':
                    tokens[i] = params[0]
                    params = params[1:]
        
        if self.in_transaction == False:
            self.__start_transaction()
        
        # if self.working_database is None:
        #     self.database = self.real_database
        # else:
        self.database = self.working_database
            
        out = []
        
        match tokens[0]:
        
            case "BEGIN":
                        
                if self.working_database is not None and self.in_transaction:
                    raise Exception("Transaction not initated")
                
                self.in_transaction = True
                # Pick tranaction mode, default 0
                match tokens[1]:
                    case "IMMEDIATE":
                        self.transaction_mode = 1
                        self.add_lock(RESERVED)
                    case "EXCLUSIVE":
                        self.transaction_mode = 2
                        self.add_lock(EXCLUSIVE)
                
            
            case "COMMIT":
                    
                if not self.in_transaction:
                    raise Exception("Transaction not initated")
                
                # Check to see if we have a reserved lock
                for lock in self.locks_held:
                    if lock.level >= RESERVED:
                        self.add_lock(EXCLUSIVE)
                        break
                
                self.__commit()
                self.in_transaction = False
                
            case "ROLLBACK":
                assert tokens[1]  == "TRANSACTION"
                
                if not self.in_transaction:
                    raise Exception("Transaction not initated")
                
                self.__rollback()
                self.in_transaction = False
                
            
            case "CREATE":
                
                if tokens[1] == "VIEW":
                    self.database.views[tokens[2]] = tokens
                else:
                
                
                    assert tokens[1] == "TABLE"
                    table_name = tokens[2] 
                    
                    if tokens[2] == "IF" and tokens[3] == "NOT" and tokens[4] == "EXISTS":
                        return []
                    
                    assert tokens[3] == "("
                    tokens = tokens[4:]
                    
                    if table_name in self.database.tables:
                        raise Exception('Table already exists')
                    
                    column_headers = []
                    
                    # Loop through tokens by column name and type (i+=2) not including the closing ) and ;
                    while 1:
                        
                        if tokens[0] == ',':
                            tokens = tokens[1:]
                            continue
                        
                        if tokens[0] == ')':
                            tokens = tokens[1:]
                            break
                        
                        column_name = tokens[0]
                        column_type = tokens[1]
                        tokens = tokens[2:]
                        
                        default = None
                        if tokens[0] == "DEFAULT":
                            tokens = tokens[1:]
                            
                            match column_type:
                                case "REAL":
                                    if tokens[0] is not None:
                                        tokens[0] = float(tokens[0])
                                case "INTEGER": # The way the real one (who cannot be named) handles this really weirdly
                                    if tokens[0] is not None and int(tokens[0]) == tokens[0]:
                                        tokens[0] = int(tokens[0])
                                        
                            default = tokens[0]
                            tokens = tokens[1:]
                        
                        column_headers.append((column_name, column_type, default))
                        
                        
                    # Create table and add it to the database
                    # new_table = Table(table_name, column_headers)
                    self.database.add_table(table_name, column_headers)
                    
                    # print(self.database.tables)
                
            
            case "INSERT":
                self.add_lock(RESERVED)
                
                assert tokens[1] == "INTO"
                tokens = tokens[2:]
                
                if tokens[0] not in self.database:
                    print(tokens[0], tokens)
                    print(self.database.tables)
                    assert tokens[0] in self.database
                table = self.database[tokens[0]]
                tokens = tokens[1:]
                
                
                insert_columns = []
                default = False
                
                if tokens[0] != "VALUES":
                    while 1:
                        if tokens[0] == '(' or tokens[0] == ',':
                            tokens = tokens[1:]
                            continue
                        
                        if tokens[0] == "DEFAULT":
                            default = True
                            tokens = tokens[1:]
                            break
                        
                        if tokens[0] == ')':
                            tokens = tokens[1:]
                            break
                        
                        insert_columns.append(tokens[0])
                        tokens = tokens[1:]
                
                assert tokens[0] == "VALUES"
                tokens = tokens[1:]
                
                if default:
                    rows = [[i[-1] for i in table.column_headers]]
                else:
                    rows = []                
                    # Get all values for each row
                    while 1:
                        values = []
                        
                        if tokens[0] == ',':
                            tokens = tokens[1:]
                            continue
                        
                        if tokens[0] == ';':
                            break
                        
                        value_i = 0
                        while 1:
                            
                            if tokens[0] == '(' or tokens[0] == ',':
                                tokens = tokens[1:]
                                continue
                            
                            if tokens[0] == ')':
                                tokens = tokens[1:]
                                break
                            
                            if len(insert_columns) == 0:
                                col_type = table.column_headers[value_i][1]
                            else:
                                col_type = table.column_headers[table.header_index[insert_columns[value_i]]][1]
                                
                            # Handle 3 being 3.0 and vise versa
                            match col_type:
                                case "REAL":
                                    if tokens[0] is not None:
                                        tokens[0] = float(tokens[0])
                                case "INTEGER": # The way the real one (who cannot be named) handles this really weirdly
                                    if tokens[0] is not None and int(tokens[0]) == tokens[0]:
                                        tokens[0] = int(tokens[0])
                            
                            values.append(tokens[0])
                            tokens = tokens[1:]
                            value_i +=1
                        
                        rows.append(values)
                    
                table.add_rows(rows, insert_columns)
            
                    
            case "SELECT":
                self.add_lock(SHARED)
                
                out = self.database.get_data(*self.database.select_decoder(tokens))
            
            case "UPDATE":
                self.add_lock(RESERVED)
                
                return_columns = []
                
                assert tokens[1] in self.database
                assert tokens[2] == "SET"
                
                table = self.database[tokens[1]]   
                
                tokens = tokens[3:]
                
                column_headers = []
                values = []
                # Get column headers and values
                while 1:
                    if tokens[0] == ',':
                        tokens = tokens[1:]
                        continue
                    
                    if tokens[0] == "WHERE" or tokens[0] == ';':
                        break
                    
                    assert tokens[1] == '='
                    
                    column_headers.append(tokens[0])
                    values.append(tokens[2])
                    
                    tokens = tokens[3:]
        
                self.database.set_data(column_headers,values,tokens, table)
            
            case "DELETE":
                self.add_lock(RESERVED)
                
                assert tokens[1] == "FROM"
                self.database.remove_data(tokens[3:], self.database[tokens[2]])
            
            case "DROP":
                #Little bobby tables
                assert tokens[1] == "TABLE"
                
                if tokens[2] == "IF" and tokens[3] == "EXISTS":
                    if tokens[4] in self.database.tables:
                        del self.database.tables[tokens[4]]
                    
                elif tokens[2] not in self.database.tables:
                        raise Exception('Table does not exist')
                
                else:
                    del self.database.tables[tokens[2]]      
        
        
        if not self.in_transaction:
            self.__commit()
        return out           
    
        

    def close(self):
        """
        Empty method that will be used in future projects
        """
        pass


def connect(database, timeout = 0, isolation_level = 0):
    """
    Creates a Connection object with the given filename
    """
    return Connection(database)


class Database:
        
    ###### LOCKS ######
    # 0 - shared lock
    # 1 - reserved lock
    # 2 - exclusive lock
    
    def __init__(self, name):
        self.name = name
        self.real = None
        self.tables = {}
        self.views = {}
        self.locks = []
    
    def __getitem__(self, key):
        return self.tables[key]
    
    def __contains__(self,key):
        return key in self.tables
    
    def __setitem__(self, key, item):
        self.tables[key] = item
        
    def create_view(self, tokens):
        view_name = tokens[2]
                    
        tokens = tokens[4:]
        assert tokens[0] == "SELECT"
        
        decoded = self.select_decoder(tokens)
        
        return_columns_mixed = decoded[0]
        order_columns = decoded[1]
        where_clause = decoded[2]
        distinct = decoded[3]
        default_table = decoded[4] 
        left_outer_join = decoded[5]
        aggregate = decoded[6]
        decending = decoded[7]
        
        
        data = self.get_data(*decoded)
        
        # Account for qualifier in return_columns  
        return_columns = self.qualify_columns(default_table, return_columns_mixed)
        
        
        column_headers = []
        for table, column in return_columns:
            if column == '*':
                [column_headers.append(i) for i in table.column_headers]
            else:
                column_headers.append(table.column_headers[table.header_index[column]])
        
        self.add_table(view_name, column_headers)
        
        self.tables[view_name].add_rows(data)
        return []
        
    def select_decoder(self, tokens):
        return_columns = []
        distinct = False
        aggregate = ""
        
        table_name = None
        # Get name of columns that will be returned
        while 1:
            # Skip ','
            if tokens[0] == ',' or tokens[0] == "SELECT": 
                tokens = tokens[1:]
                continue
            
            if tokens[0] == "MAX" or tokens[0] == "MIN":
                aggregate = tokens[0]
                return_columns.append(tokens[2])
                tokens = tokens[4:]
                continue
            
            # Catch DISTINCT
            if tokens[0] == "DISTINCT":
                distinct = True
                tokens = tokens[1:]
                continue
            
            # Stop at FROM
            if tokens[0] == "FROM":
                if tokens[1] == '(':
                    table_name = tokens[2]
                    tokens = tokens[3:]
                else:
                    table_name = tokens[1]
                    tokens = tokens[2:]
                break
            
            return_columns.append(tokens[0])
            tokens = tokens[1:]
            
        if table_name in self.views:
            self.create_view(self.views[table_name])
        
        assert table_name in self.tables
        table = self.tables[table_name]
        
        left_outer_join = []
        # Catch LEFT OUTER JOIN
        if tokens[0] == "LEFT":
            assert tokens[1] == "OUTER"
            assert tokens[2] == "JOIN"
            tokens = tokens[3:]
            
            right_table = tokens[0]
            assert tokens[1] == "ON"
            left_column = tokens[2]
            right_column = tokens[4]
            tokens = tokens[5:]
            left_outer_join = [table_name, right_table, left_column, right_column]
                            
        # Get WHERE clause
        where_clause = []
        while 1:
            if tokens[0] == "ORDER" or tokens[0] == ';':
                break
            
            where_clause.append(tokens[0])
            tokens = tokens[1:]
                
        # Get ORDER BY columns
        decending = False
        order_columns = []
        while 1:
            if tokens[0] == "ORDER" or tokens[0] == "BY"  or tokens[0] in ',()':
                tokens = tokens[1:]
                continue
            if tokens[0] == ';':
                break
            
            column = tokens[0]
            tokens = tokens[1:]
            
            if tokens[0] == "DESC":
                tokens = tokens[1:]
                if not decending:
                    decending = True
                    
            order_columns.append(column)
                
        return [return_columns, order_columns, where_clause, distinct, table, left_outer_join, aggregate, decending]
    
    def qualify_columns(self, default_table, columns):
        # Account for qualifier in return_columns  
        return_columns = []
        for column in columns:
            if '.' not in column:
                return_columns.append((default_table, column))
            else:
                dot_index = column.index('.')
                table = self.tables[column[:dot_index]]
                column_name = column[dot_index + 1:]
                return_columns.append((table, column_name))
        return return_columns
        
    def set_lock(self, conn_number, lock_level):
        lock = Lock(conn_number, lock_level)
                
        if len(self.real.locks) == 0 or self.check_locks(conn_number, lock_level):
            insort(self.real.locks, lock)
            return lock
        
    def check_locks(self, conn_number, action_level):
        
        while self.real.locks[-1].committed:
            self.real.locks.pop()
            
            if len(self.real.locks) == 0:
                return True
        
        highest = None
        i = -1
        while len(self.real.locks) + i >= 0:
            if self.real.locks[i].conn_number != conn_number and not self.real.locks[i].committed:
                highest = self.real.locks[i]
                break
            i -= 1
        
        if highest is None:
            return True
        
        if (action_level == SHARED or highest < RESERVED) and action_level < EXCLUSIVE:
            return True
        
        raise Exception("Action cannot be preformed due to locking")
        
        
    def add_table(self, table_name, column_headers):
        self.tables[table_name] = Table(table_name, column_headers)
        
    def where(self, where_clause, default_table):
        assert where_clause[0] == "WHERE"
        
        test_table = default_table
        test_column = where_clause[1]   
        test_value = where_clause[3]
        
        # Handle qualifier
        if '.' in test_column:
            dot_index = test_column.index('.')
            table = self.tables[test_column[:dot_index]]
            
            test_column = test_column[dot_index + 1:]
            test_table = table
        
        # Replace NULL
        if test_value == "NULL":
            test_value = None
        
        test_column = test_table.header_index[test_column]
        
        out_rows = []
        match where_clause[2]:
            case '=':
                for i in range(len(test_table.rows)):
                    if (value:=test_table.rows[i][test_column]) is not None and value == test_value:
                        out_rows.append((test_table, i))
            case "!=":
                for i in range(len(test_table.rows)):
                    if (value:=test_table.rows[i][test_column]) is not None and value != test_value:
                        out_rows.append((test_table, i))
            case '>':
                for i in range(len(test_table.rows)):
                    if (value:=test_table.rows[i][test_column]) is not None and value > test_value:
                        out_rows.append((test_table, i))
            case '<':
                for i in range(len(test_table.rows)):
                    if (value:=test_table.rows[i][test_column]) is not None and value < test_value:
                        out_rows.append((test_table, i))
            case 'IS':
                for i in range(len(test_table.rows)):
                    if test_table.rows[i][test_column] is test_value:
                        out_rows.append((test_table, i))
            case 'IS NOT':
                for i in range(len(test_table.rows)):
                    if test_table.rows[i][test_column] is not test_value:
                        out_rows.append((test_table, i))
        return out_rows
    
    def left_outer_join(self, join_data):
        # [left_table, right_table, left_column, right_column]
        left_table = self.tables[join_data[0]]
        right_table = self.tables[join_data[1]]
        left_column_i = left_table.header_index[join_data[2][join_data[2].index('.') + 1:]]
        right_column_i = right_table.header_index[join_data[3][join_data[3].index('.') + 1:]]
        
        # Get headers from both tables
        headers = [("".join([left_table.name, '.', header[0]]), header[1], header[2]) for header in left_table.column_headers]
        left_headers = [header[0] for header in headers] # Save for later
        headers.extend([("".join([right_table.name, '.', header[0]]), header[1], header[2]) for header in right_table.column_headers])
        
        # Create fake table to use for joined data
        temp_table = Table("temp", headers)
        
        for left_row in left_table.rows:
            
            if (value:=left_row[left_column_i]) is not None:
                last_len = len(temp_table.rows)
                
                for right_row in right_table.rows:
                    if value == right_row[right_column_i]:
                        temp_table.add_row(left_row.data + right_row.data)
                        break
                    
                if len(temp_table.rows) == last_len:
                    temp_table.add_row(left_row.data, left_headers)
               
        return temp_table
        

    def set_data(self, column_names, values, where_clause, default_table):
        
        columns = []
        for name in column_names:
            if '.' not in name:
                columns.append((default_table, default_table.header_index[name]))
            else:
                dot_index = name.index('.')
                table = self.tables[name[:dot_index]]
                column_index = table.header_index[dot_index + 1:]
                columns.append((table, column_index))
                
        
        if where_clause[0] == "WHERE":
            valid_rows = self.where(where_clause, default_table)
            for table, i in valid_rows:
                for j in range(len(columns)):
                    table.rows[i][columns[j][1]] = values[j]
        else:
            for i in range(len(default_table.rows)):
                for j in range(len(columns)):
                    columns[j][0].rows[i][columns[j][1]] = values[j]
                    
                    
    # Gets specified columns ordered by a specified column
    def get_data(self, return_columns_mixed, order_columns_mixed, where_clause, distinct, default_table, left_outer_join_data=[], aggregate="", decending = False):
        
        # Account for qualifier in ordered_columns
        order_columns = self.qualify_columns(default_table, order_columns_mixed)
        
        # Account for qualifier in return_columns  
        return_columns = self.qualify_columns(default_table, return_columns_mixed)
                
        if len(aggregate) > 0:
            return [return_columns[0][0].aggregate(aggregate, return_columns[0][1])]
            
        
        # Handle Join
        if len(left_outer_join_data) > 0:
            out = []
            join_table = self.left_outer_join(left_outer_join_data)
            
            sort_indices = []
            for column in order_columns:
                sort_indices.append(join_table.header_index['.'.join([column[0].name, column[1]])])
            
            for row in sorted(join_table.rows, key=operator.itemgetter(*sort_indices), reverse=decending):
                out_row = []
                for table, column_name in return_columns:
                    out_row.append(row[join_table.header_index['.'.join([table.name, column_name])]])
                out.append(tuple(out_row))
            return out
            
        
        # Handle WHERE
        valid_rows_mixed = []
        valid_rows = default_table.rows
        if len(where_clause) > 0 and where_clause[0] == "WHERE":
            valid_rows = []
            
            for table, i in self.where(where_clause, default_table):
                valid_rows_mixed.append((table,i))
                
            for row in valid_rows_mixed:
                valid_rows.append(row[0].rows[row[1]])
        
        # Handle DISTINCT
        if distinct:
            new_rows = []
            order_i = order_columns[0][0].header_index[order_columns[0][1]]
            for row in valid_rows:
                valid = True
                for unique_row in new_rows:
                    if row[order_i] == unique_row[order_i]:
                        valid = False
                        
                if valid:
                    new_rows.append(row)
                    
            valid_rows = new_rows
            
        # Get index of each order by column
        sort_indices = []
        for column in order_columns:
            sort_indices.append(column[0].header_index[column[1]])
        
        sorted_rows = valid_rows
        if len(sort_indices) > 0:
            sorted_rows.sort(key=operator.itemgetter(*sort_indices), reverse=decending)
        
        # Getting specified rows
        out = []
        for row in sorted_rows:
            out_row = []
            
            # Add value from each specified column to out_row
            for column in return_columns:
                if column[1][-1] == '*':
                    out_row += row
                else:
                    out_row.append(row[column[0].header_index[column[1]]])
            
            out.append(tuple(out_row))
            
                    
        return out
    
    # Remove rows
    def remove_data(self, where_clause, default_table):
        
        if where_clause[0] == "WHERE":
            for table, i in reversed(self.where(where_clause, default_table)):
                del table.rows[i]
        else:
            default_table.rows = []
                    
    

class Table:
    # # Name of the table 
    # name = ""
    
    # # List of tuples storing columns_headers and type(name, type)
    # column_headers = []
    
    # # Dictionary holding index of columns by header name
    # header_index = {}
    
    # # List of rows
    # rows = []
    
    def __init__(self, name, column_headers):
        self.name = name
        self.column_headers = column_headers
        self.rows = []
        
        self.header_index = {}
        for i in range(len(column_headers)):
            self.header_index[column_headers[i][0]] = i
    
    def __str__(self):
        return str(self.rows)
    
    
    # Add a row to the table
    def add_row(self, data, insert_columns=[]):
        if len(insert_columns) == 0:
            self.rows.append(Row(data))
        else:
            row_data = []
            
            for column in self.column_headers:
                row_data.append(column[-1])
            
            for i in range(len(insert_columns)):
                row_data[self.header_index[insert_columns[i]]] = data[i]
                
                    
            self.rows.append(Row(row_data))
               
    
    # Add several rows to the table
    def add_rows(self, data_entries, insert_columns=[]):
        for data in data_entries:
            self.add_row(data, insert_columns)
            
    def aggregate(self, agg, column):
        
        match agg:
            case "MAX":
                return tuple([sorted(self.rows, key=operator.itemgetter(self.header_index[column]))[-1][self.header_index[column]]])
            case "MIN":
                return tuple([sorted(self.rows, key=operator.itemgetter(self.header_index[column]))[0][self.header_index[column]]])
            
            
            
            
    

class Row:
    
    # # Inner data structure for the row
    # data = []

    def __init__(self, data):
        self.data = list(data)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return repr(self.data)

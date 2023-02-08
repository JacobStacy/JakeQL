"""
Name: Jacob Stacy
Netid: stacyjac
PID: 
How long did this project take you?


Sources:

"""
import string

_ALL_DATABASES = {}

class Tokenizer():
    def collect_characters(self, query, allowed_characters):
        letters = []
        for letter in query:
            if letter not in allowed_characters:
                break
            letters.append(letter)
        return "".join(letters)


    def remove_leading_whitespace(self, query, tokens):
        whitespace = self.collect_characters(query, string.whitespace)
        return query[len(whitespace):]


    def remove_word(self, query, tokens):
        word = self.collect_characters(query, string.ascii_letters + "_" + string.digits)
        if word == "NULL":
            tokens.append(None)
        else:
            tokens.append(word)
        return query[len(word):]


    def remove_text(self, query, tokens):
        assert query[0] == "'"
        query = query[1:]
        end_quote_index = query.find("'")
        text = query[:end_quote_index]
        tokens.append(text)
        query = query[end_quote_index + 1:]
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
            if query[0] in (string.ascii_letters + "_"):
                query = self.remove_word(query, tokens)
                continue

            # Handle misc char
            if query[0] in "(),;*":
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

class Connection(object):
    
    database = None
    
    
    def __init__(self, filename):
        """
        Takes a filename, but doesn't do anything with it.
        (The filename will be used in a future project).
        """
        # Temporary implementation
        _ALL_DATABASES["database1"] = Database()
        self.database = _ALL_DATABASES["database1"]

    def execute(self, statement):
        """
        Takes a SQL statement.
        Returns a list of tuples (empty unless select statement
        with rows to return).
        """
        
        tokens = Tokenizer().tokenize(statement)
        
        match tokens[0]:
            case "CREATE":
                assert tokens[1] == "TABLE"
                table_name = tokens[2] 
                assert tokens[3] == "("
                
                column_headers = []
                
                # Loop through tokens by column name and type (i+=2) not including the closing ) and ;
                for i in range(4, 4 + len(tokens[4:-2]), 3):
                    column_name = tokens[i]
                    column_type = tokens[i+1]
                    column_headers.append((column_name, column_type))
                    
                # Create table and add it to the database
                new_table = Table(table_name, column_headers)
                self.database[table_name] = new_table
                
                return None
            
            case "INSERT":
                assert tokens[1] == "INTO"
                table_name = tokens[2]
                assert table_name in self.database
                assert tokens[3] == "VALUES"
                
                row = []
                # Loop through tokens not including the closing ) and ;
                for i in range(5, 5 + len(tokens[5:-2]), 2):
                    row.append(tokens[i])
                    
                self.database[table_name].add_row(tuple(row))
                
                return None
            
            case "SELECT":
                
                return_columns = []
                
                table_name_index = None
                # Get name of columns that will be returned
                for i in range(1, len(tokens)):
                    # Skip ','
                    if tokens[i] == ',': continue
                    
                    # Stop at FROM
                    if tokens[i] == "FROM": 
                        table_name_index = i + 1 # Grab table name index
                        break
                    
                    return_columns.append(tokens[i])
                
                assert tokens[table_name_index] in self.database
                
                orderby_offset = table_name_index + 1
                if tokens[table_name_index + 1] == "ORDER" and tokens[table_name_index + 2] == "BY":
                    orderby_offset = table_name_index + 3
                    
                
                order_columns = []
                # Get ORDER BY columns
                for token in tokens[orderby_offset : -1]:
                    if token == ',': continue # Skip ','
                    order_columns.append(token)
                    
                
                return self.database[tokens[table_name_index]].get_data(return_columns, order_columns)
            

    def close(self):
        """
        Empty method that will be used in future projects
        """
        pass


def connect(filename):
    """
    Creates a Connection object with the given filename
    """
    
    return Connection(filename)


class Database():
    
    # Dictionary of tables in the database
    tables = {}
    
    def __getitem__(self, key):
        return self.tables[key]
    
    def __contains__(self,key):
        return key in self.tables
    
    def __setitem__(self, key, item):
        self.tables[key] = item
    

    


class Table():
    # Name of the table 
    name = ""
    
    # List of tuples storing columns_headers and type(name, type)
    column_headers = []
    
    # Dictionary holding index of columns by header name
    header_index = {}
    
    # List of rows
    rows = []
    
    def __init__(self, name, column_headers):
        self.name = name
        self.column_headers = column_headers
        
        for i in range(len(column_headers)):
            self.header_index[column_headers[i][0]] = i
    
    def __str__(self):
        return str(self.rows)
    
    # Add a row to the table
    def add_row(self, data):
        self.rows.append(Row(data))
    
    # Add several rows to the table
    def add_rows(self, data_entries):
        for data in data_entries:
            self.rows.append(Row(data))
            
    # Gets specified columns ordered by a specified column
    def get_data(self, return_columns, order_columns):
        
        sorted_rows = self.rows
        
        # Sort by order_columns in reverse order
        for i in range(1,len(order_columns) + 1):
            # Get index of column to sort by
            sort_index = self.header_index[order_columns[-i]]
            sorted_rows = sorted(self.rows, key=lambda a : a[sort_index])
        
        # Getting all rows
        if return_columns[0] == '*':
            return sorted_rows
        
        # Getting specified rows
        out = []
        for row in sorted_rows:
            out_row = []
            
            # Add value from each specified column to out_row
            for column in return_columns: out_row.append(row[self.header_index[column]])
            
            out.append(tuple(out_row))
            
        return out
            

class Row():
    
    # Inner data structure for the row
    data = ()

    def __init__(self, data):
        self.data = tuple(data)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return repr(self.data)


# # Testing
# sqler = connect("file")

# sqler.execute("CREATE TABLE student (name TEXT, grade REAL, piazza INTEGER);")
# sqler.execute("INSERT INTO student VALUES ('James', 4.0, 1);")
# sqler.execute("INSERT INTO student VALUES ('Yaxin', 4.0);")
# sqler.execute("INSERT INTO student VALUES ('Li', 3.2, 1);")
# print(sqler.execute("SELECT name, grade FROM student ORDER BY name;"))
# print("All:")
# print(sqler.execute("SELECT * FROM student;"))

# pass


import string

query = " INSERT   INTO instructors VALUES('James', 29, 17.5, NULL);"
query = " SELECT * FROM students"
query = "INSERT INTO student2 VALUES ('James', 3.5, 1);"


correct_tokens = [
    "INSERT",
    "INTO",
    "instructors",
    "VALUES",
    "(",
    "James",
    ",",
    29,
    ",",
    17.5,
    ",",
    None,
    ")",
    ";"
]

def collect_characters(query, allowed_characters):
    letters = []
    for letter in query:
        if letter not in allowed_characters:
            break
        letters.append(letter)
    return "".join(letters)


def remove_leading_whitespace(query, tokens):
    whitespace = collect_characters(query, string.whitespace)
    return query[len(whitespace):]


def remove_word(query, tokens):
    word = collect_characters(query,
                              string.ascii_letters + "_" + string.digits)
    if word == "NULL":
        tokens.append(None)
    else:
        tokens.append(word)
    return query[len(word):]


def remove_text(query, tokens):
    assert query[0] == "'"
    query = query[1:]
    end_quote_index = query.find("'")
    text = query[:end_quote_index]
    tokens.append(text)
    query = query[end_quote_index + 1:]
    return query

def remove_number(query, tokens):
    assert query[0] in string.digits
    
    # Grab all digits to the end or to a '.'
    num1 = collect_characters(query, string.digits)
    query = query[len(num1):]
    
    # Check if float 
    if query[0] != '.':
        tokens.append(int(num1)) # Add int
    else:
        
        # Collect and remove after '.'
        num2 = collect_characters(query, string.digits + '.')
        query = query[len(num2):]
        
        tokens.append(float(num1 + num2)) # Add float
    
    return query


def tokenize(query):
    tokens = []
    while query:
        print("Query:{}".format(query))
        print("Tokens: ", tokens)
        old_query = query

        # Handle whitespace
        if query[0] in string.whitespace:
            query = remove_leading_whitespace(query, tokens)
            continue

        # Handle keywords
        if query[0] in (string.ascii_letters + "_"):
            query = remove_word(query, tokens)
            continue

        # Handle misc char
        if query[0] in "(),;*":
            tokens.append(query[0])
            query = query[1:]
            continue

        # Handle text
        if query[0] in "'":
            query = remove_text(query, tokens)
            continue
        
        # Handle numbers
        if query[0] in string.digits:
            query = remove_number(query, tokens)
            continue
        #todo integers, floats, misc. query stuff (select * for example)

        if len(query) == len(old_query):
            raise AssertionError("Query didn't get shorter.")

    return tokens

tokens = tokenize(query)
print(tokens)
# print(correct_tokens)

print(tokens == correct_tokens)
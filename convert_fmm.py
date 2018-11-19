# Project to create a new Feature Model out of the FMM

# Approach:
#   1) Parse FMM.txt which contains tab separated file of keywords
#   2) Build list of keywords using FMM GUI items as psuedo-features
#   3) Link all keywords (psuedo and real) with feature type
#   4) Output a new FMM.txt file that can be read with the GUI

import sqlite3
import csv

sqldbfile = 'FMM.db'
csvfile = 'FMM.txt'     # Using csv reader for tab separated file

# Set of db query text
db_drop_tables =  [ \
    "DROP TABLE IF EXISTS Keywords", \
    "DROP TABLE IF EXISTS Records" \
    ]

db_create_tables = [ \
    "CREATE TABLE Keywords (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT," \
        "level INTEGER, " \
        "parent_id INTEGER," \
        "keyword TEXT," \
        "keyword_name TEXT," \
    "UNIQUE (keyword)" \
        "FOREIGN KEY(parent_id) REFERENCES Keywords(id)" \
    ");", \
    "CREATE TABLE Records (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT," \
        "processed BOOLEAN, " \
        "tab TEXT," \
        "function TEXT," \
        "keyword_name TEXT," \
        "keyword TEXT," \
        "dependencies TEXT," \
        "rule_type TEXT," \
        "min INTEGER," \
        "max INTEGER," \
        "notes TEXT" \
    ");" \
    ]

db_insert_record = \
    "INSERT OR IGNORE INTO Records " \
    "(tab, function, keyword_name, keyword, dependencies, " \
    "rule_type, min, max, notes) " \
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

db_select_data = \
    "SELECT id FROM Keywords WHERE keyword = ?"

db_select_distinct_tabs = \
    "SELECT DISTINCT tab FROM records ORDER BY tab"

db_select_distinct_functions = \
    "SELECT DISTINCT function " \
    "FROM records " \
    "WHERE tab = ?" \
    "ORDER BY function"

db_select_keywords = \
    "SELECT keyword " \
    "FROM records " \
    "WHERE tab = ? and function = ?" \
    "ORDER BY keyword"

db_select_OR_keywords_I = \
    "SELECT count(keyword) as count, tab, function, keyword " \
    "FROM records " \
    "GROUP BY tab, function, keyword " \
    "HAVING count(tab) > 1 " \
    "ORDER BY tab, function, keyword;"





# db_select_OR_keywords_II
#
# db_select_OPT_keywords_III
#




# Set up sqlite database
con = sqlite3.connect(sqldbfile)
cur = con.cursor()
for query in db_drop_tables:
    cur.execute(query)
for query in db_create_tables:
    cur.execute(query)

# Store a record from the FMM
def addRecord(record_data):
    cur.execute(db_insert_record, (record_data))

# Add new keyword to table if not exists.  Return keyword ID
def addKeyword(keyWord, keywordName, parent_id):
    cur.execute(db_insert_data, (keyWord, keywordName, parent_id))
    cur.execute(db_select_data, (keyWord,))
    keyWordID = cur.fetchone()[0]
    return keyWordID

def camelCase(input_text):
    # lower case all words, split, propercase all but first word, join
    output_text = ''
    word_list = input_text.lower().split(' ')
    for num, word in enumerate(word_list):
        if num > 0:
            new_word = word.capitalize()
        else:
            new_word = word
        output_text = output_text + new_word
    return(output_text)


# CSV records; rec[0] = FM Keyword; rec[1] = list of FM Dependencies
with open(csvfile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            addRecord(row)
        line_count += 1
    print(f'Processed {line_count} lines.')
    con.commit()

# Get list of all tabs
cur.execute(db_select_distinct_tabs)
tab_rows = cur.fetchall()
for tab_row in tab_rows:
    tab = tab_row[0]

    # Get list of all functions
    cur.execute(db_select_distinct_functions, (tab,))
    function_rows = cur.fetchall()
    for function_row in function_rows:
        function = function_row[0]
        print(tab, "\t", function)

# Process all Type I ORs
# Get list of all Type I
# For each Type I, create new keywords for each input
# cur.execute(db_select_OR_keywords_I)
# for row in cur:
#     for count in range(row[0]):
#         new_keyword = row[3] + "_" + str(count)
#         print(row[1], row[2], row[3], new_keyword)


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

###### Set of db query text
db_drop_tables =  [ \
    "DROP TABLE IF EXISTS Keywords", \
    "DROP TABLE IF EXISTS Ancestors", \
    "DROP TABLE IF EXISTS Records", \
    "DROP TABLE IF EXISTS Dependencies" \
    ]

db_create_tables = [ \
    "CREATE TABLE Keywords (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "level INTEGER, " \
        "parent_id INTEGER, " \
        "keyword TEXT," \
        "keyword_name TEXT, " \
        "keyword_type TEXT CHECK( keyword_type IN ('MAN','OPT','ALT','OR')), " \
    "UNIQUE (keyword) " \
        "FOREIGN KEY(parent_id) REFERENCES Keywords(id) " \
    ");", \
    "CREATE TABLE Ancestors (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "ancestor_id INTEGER, " \
        "ancestor_name TEXT, " \
        "FOREIGN KEY(ancestor_id) REFERENCES Keywords(id) " \
    ");", \
    "CREATE TABLE Records (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "processed BOOLEAN, " \
        "tab TEXT, " \
        "function TEXT, " \
        "keyword_name TEXT, " \
        "keyword TEXT, " \
        "dependencies TEXT, " \
        "rule_type TEXT, " \
        "min INTEGER, " \
        "max INTEGER, " \
        "notes TEXT" \
    ");", \
    "CREATE TABLE Dependencies (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "processed BOOLEAN, " \
        "keyword TEXT, " \
        "feature_id INTEGER, " \
        "FOREIGN KEY(feature_id) REFERENCES Records(id) " \
    ");" \
    ]

db_insert_record = \
    "INSERT OR IGNORE INTO Records " \
    "(tab, function, keyword_name, keyword, dependencies, " \
    "rule_type, min, max, notes) " \
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'no text')"

db_insert_dependency = \
    "INSERT INTO Dependencies " \
    "(processed, keyword, feature_id) " \
    "VALUES (?, ?, ?)"

db_select_data = \
    "SELECT id FROM Keywords WHERE keyword = ?"

db_select_record = \
    "SELECT id FROM Records WHERE keyword = ?"

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

db_insert_feature = \
    "INSERT OR IGNORE INTO Keywords " \
    "(level, parent_id, keyword, keyword_name, keyword_type) " \
    "VALUES (?, ?, ?, ?, ?)"


# db_select_OR_keywords_II
#
# db_select_OPT_keywords_III
#

##### Function definitions

# Store a record from the FMM
def addRecord(record_data):
    cur.execute(db_insert_record, (record_data))
    return(cur.lastrowid)


def addDependency(keyword, feature_id):
    cur.execute(db_insert_dependency, (False, keyword, feature_id))


# Add new keyword to table if not exists.  Return keyword ID
def addKeyword(level, parent_id, keyWord, keywordName, keywordType):
    cur.execute(db_insert_feature, (level, parent_id, keyWord, keywordName, keywordType))
    cur.execute(db_select_data, (keyWord,))
    keyWordID = cur.fetchone()
    return(keyWordID)

# lower case all words, split, propercase all but first word, join
def camelCase(input_text):
    output_text = ''
    word_list = input_text.lower().split(' ')
    for num, word in enumerate(word_list):
        if num > 0:
            new_word = word.capitalize()
        else:
            new_word = word
        output_text = output_text + new_word
    return(output_text)


def removeSpecialChars(input_text):
    specials = "/"
    output_text = ''
    for char in input_text:
        if char not in specials:
            output_text = output_text + char
    return(output_text)



##### main program

# Set up sqlite database
con = sqlite3.connect(sqldbfile)
cur = con.cursor()
for query in db_drop_tables:
    cur.execute(query)
for query in db_create_tables:
    cur.execute(query)


# CSV records; rec[0] = FM Keyword; rec[1] = list of FM Dependencies
with open(csvfile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            feature_id = addRecord(row)
            dependencies = row[4].split(';') # semi-colon separated list of dependencies in row[4]
            for dependency in dependencies:
                addDependency(dependency, feature_id)
        line_count += 1
    print(f'Processed {line_count} lines.')
    con.commit()

# Get list of all tabs and create features
cur.execute(db_select_distinct_tabs)
tab_rows = cur.fetchall()
for tab_row in tab_rows:
    tabName = tab_row[0]
    tabKeyword = camelCase(removeSpecialChars(tabName))
    parentID = None
    featureLevel = 0
    keyWordType = 'MAN'
    tab_feature_id = addKeyword(featureLevel, parentID, tabKeyword, tabName, keyWordType)[0]

    # Get list of all functions and create features linked to tabs
    cur.execute(db_select_distinct_functions, (tabName,))
    function_rows = cur.fetchall()
    for function_row in function_rows:
        functionName = function_row[0]
        functionKeyword = camelCase(removeSpecialChars(functionName))
        parentID = tab_feature_id
        featureLevel = 1
        keyWordType = 'MAN'

        function_feature_id = addKeyword(featureLevel, parentID, functionKeyword, functionName, keyWordType)[0]

# Process all Type I ORs
# Get list of all Type I
# For each Type I, create new keywords for each input
# cur.execute(db_select_OR_keywords_I)
# for row in cur:
#     for count in range(row[0]):
#         new_keyword = row[3] + "_" + str(count)
#         print(row[1], row[2], row[3], new_keyword)

con.commit()

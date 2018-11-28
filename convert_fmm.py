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
def drop_tables():
    sqllist = [ \
        "DROP TABLE IF EXISTS Keywords", \
        "DROP TABLE IF EXISTS Requires", \
        "DROP TABLE IF EXISTS Records", \
        "DROP TABLE IF EXISTS Dependencies" \
        ]
    for query in sqllist:
        cur.execute(query)

def create_tables():
    sqllist =  [ \
    "CREATE TABLE Keywords (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "level INTEGER, " \
        "parent_id INTEGER, " \
        "root_id INTEGER, " \
        "keyword TEXT," \
        "keyword_name TEXT, " \
        "keyword_type TEXT CHECK( keyword_type IN ('MAN','OPT','ALT','OR')), " \
    "UNIQUE (keyword) " \
        "FOREIGN KEY(parent_id) REFERENCES Keywords(id) " \
    ");", \
    "CREATE TABLE Requires (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "requires_id INTEGER, " \
        "FOREIGN KEY(requires_id) REFERENCES Keywords(id) " \
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
    for query in sqllist:
        cur.execute(query)

############ Records and Dependencies
# Create
def addRecord(record_data):
    sql = "INSERT OR IGNORE INTO Records " \
        "(tab, function, keyword_name, keyword, dependencies, " \
        "rule_type, min, max, notes) " \
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'no text');"
    cur.execute(sql, (record_data))
    return(cur.lastrowid)

# Read
def getTabs():
    sql = "SELECT DISTINCT tab FROM records ORDER BY tab;"
    cur.execute(sql)
    return(cur.fetchall())

def getFunctions(tab):
    sql = "SELECT DISTINCT function FROM records " \
        "WHERE tab = ? ORDER BY function;"
    cur.execute(sql, (tab,))
    return(cur.fetchall())



# Update



############ Keywords and Requires
# Create
def addKeyword(level, parent_id, root_id, keyword, keyword_name, keyword_type):
    sql = "INSERT OR IGNORE INTO Keywords " \
        "(level, parent_id, root_id, keyword, keyword_name, keyword_type) " \
        "VALUES (?, ?, ?, ?, ?, ?);"
    cur.execute(sql, (level, parent_id, root_id, keyword, keyword_name, keyword_type))
    return(cur.lastrowid)

def addDependency(keyword, feature_id):
    sql = "INSERT INTO Dependencies " \
        "(processed, keyword, feature_id) " \
        "VALUES (?, ?, ?);"
    cur.execute(sql, (False, keyword, feature_id))

# Read
def getKeywordID(keyWord):
    sql = "SELECT id FROM Keywords WHERE keyword = ?;"
    cur.execute(sql, (keyWord,))
    return(cur.fetchone())[0]

def getKeywordRootID(keyWord):
    sql = "SELECT root_id FROM Keywords WHERE keyword = ?;"
    cur.execute(sql, (keyWord,))
    return(cur.fetchone())[0]

def get_all_records():
    # Return list of records
    sql = "SELECT * FROM records;"
    cur.execute(sql)
    return(cur.fetchall())

# Update
def updateRootID(root_id, keyword_id):
    # Update rootID of entry in keyword
    sql = "UPDATE Keywords SET root_id = ? " \
        "WHERE id = ?;"
    cur.execute(sql, (root_id, keyword_id))











db_select_keywords = \
    "SELECT keyword " \
    "FROM records " \
    "WHERE tab = ? and function = ?" \
    "ORDER BY keyword;"

db_select_OR_keywords_I = \
    "SELECT count(keyword) as count, tab, function, keyword " \
    "FROM records " \
    "GROUP BY tab, function, keyword " \
    "HAVING count(tab) > 1 " \
    "ORDER BY tab, function, keyword;"


db_select_keyword_root = \
    "SELECT root_id " \
    "FROM keywords" \
    "WHERE keyword = ?;"








# db_select_OR_keywords_II
#
# db_select_OPT_keywords_III
#

##### Function definitions
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

def read_fmm(file):
    # CSV records; rec[0] = FM Keyword; rec[1] = list of FM Dependencies
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                feature_id = addRecord(row)
                dependencies = row[4].split(';')  # semi-colon separated list of dependencies in row[4]
                for dependency in dependencies:
                    addDependency(dependency, feature_id)
            line_count += 1
        print(f'Processed {line_count} lines.')
        con.commit()





##### main program #####

# Set up sqlite database
con = sqlite3.connect(sqldbfile)
cur = con.cursor()
drop_tables()
create_tables()

# Load database with records from FMM.txt
read_fmm(csvfile)





# Get list of all tabs and create features
tab_rows = getTabs()
for tab_row in tab_rows:
    featureLevel = 0
    parentID = None
    rootID = None
    keywordName = tab_row[0]
    keyword = camelCase(removeSpecialChars(keywordName))
    keyWordType = 'MAN'
    tab_feature_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
    updateRootID(tab_feature_id, tab_feature_id)

    # Get list of all functions and create features linked to tabs (keywordName of tab)
    function_rows = getFunctions(keywordName)
    for function_row in function_rows:
        featureLevel = 1
        parentID = tab_feature_id
        rootID = tab_feature_id
        keywordName = function_row[0]
        keyword = camelCase(removeSpecialChars(keywordName))
        keyWordType = 'MAN'
        function_feature_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)

# Loop through all records; add keywords.  Initially set parentID = RootID.  Later will update if needed.
record_rows = get_all_records()
for record_row in record_rows:
    featureLevel = 2
    tab = record_row[2]
    tabKeyword = camelCase(removeSpecialChars(tab))
    parentID = getKeywordID(tabKeyword)
    rootID = getKeywordRootID(tabKeyword)
    keyword = record_row[5]
    keywordName = record_row[4]
    keyWordType = 'MAN'
    keyword_featue_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)

# Loop again through all records; If a dependency has same root, make the dependency
#   be the paraent of the current record, otherwise make it a requires.


# Process all Type I ORs
# Get list of all Type I
# For each Type I, create new keywords for each input
# cur.execute(db_select_OR_keywords_I)
# for row in cur:
#     for count in range(row[0]):
#         new_keyword = row[3] + "_" + str(count)
#         print(row[1], row[2], row[3], new_keyword)

con.commit()

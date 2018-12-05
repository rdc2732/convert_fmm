# Project to create a new Feature Model out of the FMM
# This file contains only the python+sql statments


###### Database Setup
def drop_tables(cursor):
    sqllist = [ \
        "DROP TABLE IF EXISTS Keywords", \
        "DROP TABLE IF EXISTS Requires", \
        "DROP TABLE IF EXISTS Records", \
        "DROP TABLE IF EXISTS Dependencies" \
        ]
    for query in sqllist:
        cursor.execute(query)

def create_tables(cursor):
    sqllist =  [ \
    "CREATE TABLE Keywords (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "level INTEGER, " \
        "parent_id INTEGER, " \
        "root_id INTEGER, " \
        "keyword TEXT," \
        "keyword_name TEXT, " \
        "keyword_type TEXT CHECK( keyword_type IN ('MAN','OPT','ALT','OR')), " \
        "min INTEGER, " \
        "max INTEGER, " \
        "notes TEXT, "\
        "UNIQUE (keyword) " \
        "FOREIGN KEY(parent_id) REFERENCES Keywords(id) " \
    ");", \
    "CREATE TABLE Requires (" \
        "requires_id INTEGER, " \
        "keywords_id INTEGER, " \
        "FOREIGN KEY(keywords_id) REFERENCES Keywords(id) " \
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
        "dependency TEXT, " \
        "record_id INTEGER, " \
        "FOREIGN KEY(record_id) REFERENCES Records(id) " \
    ");" \
    ]
    cursor.execute(sqllist[0])
    # for query in sqllist:
    #     cursor.execute(query)


############ Records and Dependencies
# Create
def addRecord(cursor, record_data):
    sql = "INSERT OR IGNORE INTO Records " \
        "(tab, function, keyword_name, keyword, dependencies, " \
        "rule_type, min, max, notes) " \
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'no text');"
    cursor.execute(sql, (record_data))
    return(cursor.lastrowid)

def addDependency(cursor, dependency, record_id):
    sql = "INSERT INTO Dependencies " \
        "(dependency, record_id) " \
        "VALUES (?, ?);"
    cursor.execute(sql, (dependency, record_id))

# Read
def getRecord(cursor, keyword):
    sql = "SELECT * FROM records " \
        "WHERE keyword = ?;"
    cursor.execute(sql, (keyword,))
    return(cursor.fetchone())

def getAllRecords(cursor):
    # Return list of records
    sql = "SELECT * FROM records;"
    cursor.execute(sql)
    return(cursor.fetchall())

def getAllRecordsAndDependencies(cursor):
    # Return list of records and dependencies
    sql = "SELECT * FROM records, dependencies " \
        "WHERE dependencies.record_id = records.id;"
    cursor.execute(sql)
    return(cursor.fetchall())

def getTabs(cursor):
    sql = "SELECT DISTINCT tab FROM records ORDER BY tab;"
    cursor.execute(sql)
    return(cursor.fetchall())

def getFunctions(cursor, tab):
    sql = "SELECT function FROM records " \
        "WHERE tab = ? ORDER BY function;"
    cursor.execute(sql, (tab,))
    return(cursor.fetchall())

def getFeatures(cursor, function):
    sql = "SELECT keyword FROM records " \
        "WHERE function = ? ORDER BY keyword;"
    cursor.execute(sql, (function,))
    return(cursor.fetchall())

def getDeps(cursor):
    sql = "SELECT DISTINCT dependency FROM Dependencies ORDER BY dependency;"
    cursor.execute(sql)
    return(cursor.fetchall())

def getDependents(cursor, keyword):
    sql = "SELECT * FROM dependencies " \
        "WHERE keyword = ? ORDER BY keyword;"
    cursor.execute(sql, (keyword,))
    return(cursor.fetchall())

# def getKeywordDependencyPairs():
#     sql = "select keywords.id as keyid, dependencies.id as depid " \
#         "from keywords, dependencies " \
#         "where dependencies.record_id = keywords.id; "
#     cursor.execute(sql)
#     return(cursor.fetchall())

# Update



############ Keywords and Requires
# Create
# def addKeyword_old(cursor, level, parent_id, root_id, keyword, keyword_name, keyword_type):
#     sql = "INSERT OR IGNORE INTO Keywords " \
#         "(level, parent_id, root_id, keyword, keyword_name, keyword_type) " \
#         "VALUES (?, ?, ?, ?, ?, ?);"
#     if keyword == 'odsDualChannel':
#         print(sql, keyword)
#     cursor.execute(sql, (level, parent_id, root_id, keyword, keyword_name, keyword_type))
#     return(cursor.lastrowid)

def addKeyword(cursor, level, parent_id, root_id, keyword, keyword_name, keyword_type, min, max):
    # Create new if necessary, return data for record
    sql = "INSERT INTO Keywords " \
        "(level, parent_id, root_id, keyword, keyword_name, keyword_type, min, max) " \
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
    cursor.execute(sql, (level, parent_id, root_id, keyword, keyword_name, keyword_type, min, max))
    new_id = cursor.lastrowid
    return(new_id)



def addRequires(cursor, requires_id, keywords_id):
    sql = "INSERT INTO Requires " \
        "(requires_id, keywords_id) " \
        "VALUES (?, ?);"
    cursor.execute(sql, (requires_id, keywords_id))

# Read
def getKeywords(cursor):
    sql = "SELECT keyword FROM Keywords;"
    cursor.execute(sql)
    list_of_tuples = cursor.fetchall()
    return([x[0] for x in list_of_tuples])

def getKeywordsData(cursor):
    sql = "SELECT * FROM Keywords;"
    cursor.execute(sql)
    return(cursor.fetchall())

def getKeywordID(cursor, keyWord):
    sql = "SELECT id FROM Keywords WHERE keyword = ?;"
    cursor.execute(sql, (keyWord,))
    result = cursor.fetchone()
    if result == None:
        return(None)
    else:
        return(result[0])

def getKeywordRootID(cursor, keyWord):
    sql = "SELECT root_id FROM Keywords WHERE keyword = ?;"
    cursor.execute(sql, (keyWord,))
    result = cursor.fetchone()
    if result == None:
        return(None)
    else:
        return(result[0])

def getKeywordRootIDfromID(cursor, keyWordID):
    sql = "SELECT root_id FROM Keywords WHERE id = ?;"
    cursor.execute(sql, (keyWordID,))
    result = cursor.fetchone()
    if result == None:
        return(None)
    else:
        return(result[0])

def getKeywordDatafromID(cursor, keyWordID):
    sql = "SELECT level, parent_id, root_id, keyword, keyword_name, keyword_type FROM Keywords WHERE id = ?;"
    cursor.execute(sql, (keyWordID,))
    result = cursor.fetchone()
    if result == None:
        return(None)
    else:
        return(result)

def getRequiresFromKeywordID(cursor, keyWordID):
    sql = "SELECT * FROM Requires WHERE keywords_id = ?;"
    cursor.execute(sql, (keyWordID,))
    return(cursor.fetchall())


# Update
def updateRootID(cursor, root_id, keyword_id):
    # Update rootID of entry in keyword
    sql = "UPDATE Keywords SET root_id = ? " \
        "WHERE id = ?;"
    cursor.execute(sql, (root_id, keyword_id))

def updateKeywordParent(cursor, keywordID,dependencyID):
    parentLevel = getKeywordDatafromID(cursor, dependencyID)[1]
    sql = "UPDATE Keywords SET parent_id = ?, level = ? " \
        "WHERE id = ?;"
    cursor.execute(sql, (dependencyID, parentLevel + 1, keywordID))

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







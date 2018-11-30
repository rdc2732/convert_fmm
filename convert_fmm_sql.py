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
    for query in sqllist:
        cursor.execute(query)


############ Records and Dependencies
# Create
def addRecord(record_data):
    sql = "INSERT OR IGNORE INTO Records " \
        "(tab, function, keyword_name, keyword, dependencies, " \
        "rule_type, min, max, notes) " \
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'no text');"
    cur.execute(sql, (record_data))
    return(cur.lastrowid)

def addDependency(dependency, record_id):
    sql = "INSERT INTO Dependencies " \
        "(dependency, record_id) " \
        "VALUES (?, ?);"
    cur.execute(sql, (dependency, record_id))

# Read
def getRecord(keyword):
    sql = "SELECT * FROM records " \
        "WHERE keyword = ?;"
    cur.execute(sql, (keyword,))
    return(cur.fetchone())

def get_all_records():
    # Return list of records
    sql = "SELECT * FROM records;"
    cur.execute(sql)
    return(cur.fetchall())

def getTabs():
    sql = "SELECT DISTINCT tab FROM records ORDER BY tab;"
    cur.execute(sql)
    return(cur.fetchall())

def getFunctions(tab):
    sql = "SELECT function FROM records " \
        "WHERE tab = ? ORDER BY function;"
    cur.execute(sql, (tab,))
    return(cur.fetchall())

def getFeatures(function):
    sql = "SELECT keyword FROM records " \
        "WHERE function = ? ORDER BY keyword;"
    cur.execute(sql, (function,))
    return(cur.fetchall())

def getDeps():
    sql = "SELECT DISTINCT dependency FROM Dependencies ORDER BY dependency;"
    cur.execute(sql)
    return(cur.fetchall())

def getDependents(keyword):
    sql = "SELECT * FROM dependencies " \
        "WHERE keyword = ? ORDER BY keyword;"
    cur.execute(sql, (keyword,))
    return(cur.fetchall())

# def getKeywordDependencyPairs():
#     sql = "select keywords.id as keyid, dependencies.id as depid " \
#         "from keywords, dependencies " \
#         "where dependencies.record_id = keywords.id; "
#     cur.execute(sql)
#     return(cur.fetchall())

# Update



############ Keywords and Requires
# Create
def addKeyword(level, parent_id, root_id, keyword, keyword_name, keyword_type):
    sql = "INSERT OR IGNORE INTO Keywords " \
        "(level, parent_id, root_id, keyword, keyword_name, keyword_type) " \
        "VALUES (?, ?, ?, ?, ?, ?);"
    cur.execute(sql, (level, parent_id, root_id, keyword, keyword_name, keyword_type))
    return(cur.lastrowid)

def addRequires(requires_id, keywords_id):
    sql = "INSERT INTO Requires " \
        "(requires_id, keywords_id) " \
        "VALUES (?, ?);"
    print(sql, requires_id, keywords_id)
    cur.execute(sql, (requires_id, keywords_id))

# Read
def getKeywords():
    sql = "SELECT keyword FROM Keywords;"
    cur.execute(sql)
    list_of_tuples = cur.fetchall()
    return([x[0] for x in list_of_tuples])

def getKeywordsData():
    sql = "SELECT * FROM Keywords;"
    cur.execute(sql)
    return(cur.fetchall())

def getKeywordID(keyWord):
    sql = "SELECT id FROM Keywords WHERE keyword = ?;"
    cur.execute(sql, (keyWord,))
    return(cur.fetchone()[0])

def getKeywordRootID(keyWord):
    sql = "SELECT root_id FROM Keywords WHERE keyword = ?;"
    cur.execute(sql, (keyWord,))
    result = cur.fetchone()
    if result == None:
        return(None)
    else:
        return(result[0])

def getKeywordRootIDfromID(keyWordID):
    sql = "SELECT root_id FROM Keywords WHERE id = ?;"
    cur.execute(sql, (keyWordID,))
    result = cur.fetchone()
    if result == None:
        return(None)
    else:
        return(result[0])

def getKeywordDatafromID(keyWordID):
    sql = "SELECT * FROM Keywords WHERE id = ?;"
    cur.execute(sql, (keyWordID,))
    result = cur.fetchone()
    if result == None:
        return(None)
    else:
        return(result)

def getRequiresFromKeywordID(keyWordID):
    sql = "SELECT * FROM Requires WHERE keywords_id = ?;"
    print(sql, keywordID)
    cur.execute(sql, (keyWordID,))
    return(cur.fetchall())


# Update
def updateRootID(root_id, keyword_id):
    # Update rootID of entry in keyword
    sql = "UPDATE Keywords SET root_id = ? " \
        "WHERE id = ?;"
    cur.execute(sql, (root_id, keyword_id))

def updateKeywordParent(keywordID,dependencyID):
    parentLevel = getKeywordDatafromID(dependencyID)[1]
    sql = "UPDATE Keywords SET parent_id = ?, level = ? " \
        "WHERE id = ?;"
    print(sql, ependencyID, parentLevel + 1, keywordID)
    cur.execute(sql, (dependencyID, parentLevel + 1, keywordID))



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







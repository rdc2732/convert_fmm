# Project to create a new Feature Model out of the FMM
# This file contains only the python+sql statments


###### Database Setup
def drop_tables(cursor):
    sqllist = [
        "DROP TABLE IF EXISTS Keywords",
        "DROP TABLE IF EXISTS Relations",
        "DROP TABLE IF EXISTS Records",
        "DROP TABLE IF EXISTS Dependencies"
        ]
    for query in sqllist:
        cursor.execute(query)

def create_tables(cursor):
    sqllist =  [
    "CREATE TABLE Records (" 
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " 
        "processed BOOLEAN, " 
        "keyword_name TEXT, " 
        "keyword TEXT, " 
        "rule_type TEXT, " 
        "tab TEXT, " 
        "function TEXT, " 
        "min INTEGER, " 
        "max INTEGER, " 
        "notes TEXT, "
        "dependencies TEXT " 
        ");",
    "CREATE TABLE Dependencies (" 
        "dependency TEXT, " 
        "record_id INTEGER, " 
        "FOREIGN KEY(record_id) REFERENCES Records(id) " 
        ");",
    "CREATE TABLE Keywords (" 
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " 
        "keyword_name TEXT, " 
        "keyword TEXT, " 
        "rule_type TEXT, " 
        "tab TEXT, " 
        "function TEXT, " 
        "min INTEGER, " 
        "max INTEGER, " 
        "notes TEXT " 
        ");",
    "CREATE TABLE Relations (" 
        "enabler_id INTEGER, " 
        "dependent_id INTEGER, " 
        "FOREIGN KEY(enabler_id) REFERENCES Records(id), " 
        "FOREIGN KEY(dependent_id) REFERENCES Records(id) " 
        ");"
    ]
    for query in sqllist:
        cursor.execute(query)






############ Records and Dependencies
# Create
def addRecord(cursor, record_data):
    sql = "INSERT OR IGNORE INTO Records " \
        "(tab, function, keyword_name, keyword, dependencies, " \
        "rule_type, min, max, notes) " \
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, '');"
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


def getAllDependencies(cursor):
    # Return list of records and dependencies
    sql = "SELECT * FROM dependencies;"
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

def addKeyword(cursor, keyword_data):
    # Create new if necessary, return data for record
    sql = "INSERT INTO Keywords " \
        "(keyword_name, keyword, rule_type, tab, function, min, max, notes) " \
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
    cursor.execute(sql, (keyword_data))
    new_id = cursor.lastrowid
    return(new_id)




def addRelation(cursor, enabler_id, dependent_id):
    sql = "INSERT INTO Relations "\
        "(enabler_id, dependent_id) "\
        "VALUES (?, ?);"
    cursor.execute(sql, (enabler_id, dependent_id))


def getAllRelations(cursor):
    sql = "SELECT * FROM Relations;"
    cursor.execute(sql)
    return(cursor.fetchall())



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

def getRootKeywordsData(cursor):
    sql = "SELECT * FROM Keywords where level = 0;"
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

def getKeywordParentIDLevel(cursor, keyWord):
    sql = "SELECT parent_id, level FROM Keywords WHERE keyword = ?;"
    cursor.execute(sql, (keyWord,))
    result = cursor.fetchone()
    if result == None:
        return(None)
    else:
        return(result)

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

def getKeywordChildrenfromID(cursor, keyWordID):
    sql = "SELECT level, parent_id, root_id, keyword, keyword_name, keyword_type, "\
            "min, max FROM Keywords WHERE parent_id = ?;"
    cursor.execute(sql, (keyWordID,))
    result = cursor.fetchall()
    if result == None:
        return (None)
    else:
        return (result)


def getRequiresFromKeywordID(cursor, keyWordID):
    sql = "SELECT * FROM Requires WHERE keywords_id = ?;"
    cursor.execute(sql, (keyWordID,))
    return(cursor.fetchall())

def getKeywordRelatedData(cursor, keyWordID):
    sql = "SELECT k1.level as level, k1.keyword as keyword, k1.keyword_name as keyword_name, "\
            "k1.keyword_type as keyword_type, k1.min as min, k1.max as max from keywords as k1 "\
            "LEFT OUTER JOIN keywords as k2 WHERE k1.id = k2.parent_id and k1.parent_id = ? "\
            "GROUP BY k1.level, k1.keyword ORDER BY k1.level, k1.keyword;"
    cursor.execute(sql, (keyWordID,))
    return(cursor.fetchall())

# Update
def updateRootID(cursor, root_id, keyword_id):
    # Update rootID of entry in keyword
    sql = "UPDATE Keywords SET root_id = ? " \
        "WHERE id = ?;"
    cursor.execute(sql, (root_id, keyword_id))


def updateParentIDLevel(cursor, keyword_id, new_parent_id, new_level):
    # Update rootID of entry in keyword
    sql = "UPDATE Keywords SET parent_id = ?, level = ? " \
        "WHERE id = ?;"
    cursor.execute(sql, (new_parent_id, new_level, keyword_id))


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

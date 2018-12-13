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
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " 
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
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " 
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
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'no text');"
    cursor.execute(sql, (record_data))
    return(cursor.lastrowid)

def addDependency(cursor, dependency, record_id):
    sql = "INSERT INTO Dependencies " \
        "(dependency, record_id) " \
        "VALUES (?, ?);"
    cursor.execute(sql, (dependency, record_id))







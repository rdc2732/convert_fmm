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
db_drop_tables =  \
    "DROP TABLE IF EXISTS Keywords"

db_create_tables = \
    "CREATE TABLE Keywords (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT," \
        "parent_id INTEGER," \
        "keyword TEXT," \
        "keyword_name TEXT," \
    "UNIQUE (keyword)" \
        "FOREIGN KEY(parent_id) REFERENCES Keywords(id)" \
    ")"

db_insert_data = \
    "INSERT OR IGNORE INTO Keywords " \
    "(keyword, keyword_name, parent_id) " \
    "VALUES (?, ?, ?)"

db_select_data = \
    "SELECT " \
        "id " \
    "FROM " \
        "Keywords WHERE keyword = ?"


# Set up sqlite database
con = sqlite3.connect(sqldbfile)
cur = con.cursor()
cur.execute(db_drop_tables)
cur.execute(db_create_tables)


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
        new_id = addKeyword(camelCase(row[0]),row[1],None)
        # if line_count > 0:
        #     keyword_id = addKeyword(row[3])
        #     dependency_list = row[4].split(';')
        #     while '' in dependency_list: # Remove unfortunate trailing '' elements
        #         dependency_list.remove('')
        #     for dependency in dependency_list:
        #         dependency_id = addKeyword(dependency)
        #         addDependency(dependency_id, keyword_id)
        line_count += 1
    print(f'Processed {line_count} lines.')


con.commit()

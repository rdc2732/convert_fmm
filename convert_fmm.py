# Project to create a new Feature Model out of the FMM

# Approach:
#   1) Parse FMM.txt which contains tab separated file of keywords
#   2) Build list of keywords using FMM GUI items as psuedo-features
#   3) Link all keywords (psuedo and real) with feature type
#   4) Output a new FMM.txt file that can be read with the GUI

import sqlite3
import csv
from convert_fmm_sql import *

sqldbfile = 'FMM.db'
csvfile = 'FMM.txt'     # Using csv reader for tab separated file

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
drop_tables(cur)
create_tables(cur)

# Load database with records from FMM.txt
read_fmm(csvfile)





# Get list of all tabs and create features
tab_rows = getTabs()
for tab_row in tab_rows:
    featureLevel = 0
    parentID = 0
    rootID = 0
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

        # Get list of all keywords and create features linked to functions (keywordName of function)
        feature_rows = getFeatures(keywordName)
        for feature_row in feature_rows:
            featureLevel = 2
            parentID = function_feature_id
            rootID = tab_feature_id
            keywordName = feature_row[0]
            keyword = camelCase(removeSpecialChars(keywordName))
            keyWordType = 'MAN'
            feature_feature_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
con.commit()

# Create new "tab" for Common features
featureLevel = 0
parentID = 0
rootID = 0
keywordName = "Common Features"
keyword = camelCase(removeSpecialChars(keywordName))
keyWordType = 'MAN'
common_feature_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
updateRootID(common_feature_id, common_feature_id)
con.commit()

# Create new "functions" for Common features
dep_rows = getDeps()
for dep_row in dep_rows:
    dependency = dep_row[0]
    if dependency.find("Common") == 0:
        featureLevel = 1
        parentID = common_feature_id
        rootID = common_feature_id
        keywordName = dependency
        keyword = camelCase(removeSpecialChars(keywordName))
        keyWordType = 'MAN'
        dep_feature_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
con.commit()

# Create new "features" for any other dependencies
key_rows = getKeywords()
for dep_row in dep_rows:
    keywordName = dep_row[0]
    keyword = camelCase(removeSpecialChars(keywordName))
    if keyword not in key_rows:
        featureLevel = 0
        parentID = 0
        rootID = 0
        keyWordType = 'MAN'
        dep_feature_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
        updateRootID(dep_feature_id, dep_feature_id)
con.commit()


# # Loop through all records; add keywords.  Initially set parentID = RootID.  Later will update if needed.
# record_rows = get_all_records()
# for record_row in record_rows:
#     featureLevel = 2
#     tab = record_row[2]
#     tabKeyword = camelCase(removeSpecialChars(tab))
#     parentID = getKeywordID(tabKeyword)
#     rootID = getKeywordRootID(tabKeyword)
#     keyword = record_row[5]
#     keywordName = record_row[4]
#     keyWordType = 'MAN'
#     keyword_featue_id = addKeyword(featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
#


# Loop through all keywords and requires. If a require has same root, make the require
#   be the paraent of the current keyword, ane remove from requires for that keyword.

allKeywordRows = getKeywordsData()
for keywordRow in allKeywordRows:
    keywordID = keywordRow[0]
    keyword = keywordRow[4]
    requiresRows = getRequiresFromKeywordID(keywordID)
    for requiresRow in requiresRows:
        print(keywordID, requiresRow)
    # if getKeywordRootIDfromID(keywordID) == getKeywordRootIDfromID(dependencyID):
    #     updateKeywordParent(keywordID, dependencyID)
    # else:
    #     addRequires(dependencyID, keywordID)
con.commit()

    # keyword = record_row[5]
    # print('\n', keyword)
    # dependent_rows = getDependents(keyword)
    # for dependent_row in dependent_rows:
    #     dependent = dependent_row[2]
    #     print('\t', dependent)
        # dependentRootID = getKeywordID(dependent)
        # parentID = dependent_row[3]
        # print(dependent, dependentRootID)
        #
        # parentRootID = getKeywordRootIDfromID(parentID)
        # print(parentRootID)


# Process all Type I ORs
# Get list of all Type I
# For each Type I, create new keywords for each input
# cur.execute(db_select_OR_keywords_I)
# for row in cur:
#     for count in range(row[0]):
#         new_keyword = row[3] + "_" + str(count)
#         print(row[1], row[2], row[3], new_keyword)


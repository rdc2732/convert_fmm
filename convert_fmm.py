# Project to create a new Feature Model out of the FMM

# Approach:
#   1) Parse FMM.txt which contains tab separated file of keywords
#   2) Build list of keywords using FMM GUI items as psuedo-features
#   3) Link all keywords (psuedo and real) with feature type
#   4) Output a new FMM.txt file that can be read with the GUI

import sqlite3
import csv
import re
from convert_fmm_sql import *

sqldbfile = 'FMM.db'
csvfile = 'FMM.txt'     # Using csv reader for tab separated file

##### Function definitions
# Uncamelcase words, needed to standardize the input data that does not follow rules
# Returns string with parts separated by '_'
def uncamelcase(input_text):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', input_text)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return(s2)

# lower case all words, split, propercase all but first word,
# join; if only one word return with original caps
def camelCase(input_text):
    output_text = ''
    word_list = input_text.split(' ')
    if len(word_list) == 1:
        word_list = uncamelcase(word_list[0]).split('_')
    for num, word in enumerate(word_list):
        new_word = word.lower()
        if num > 0:
            new_word = word.capitalize()
        output_text = output_text + new_word
    return(output_text)

def removeSpecialChars(input_text):
    specials = "/"
    output_text = ''
    for char in input_text:
        if char not in specials:
            output_text = output_text + char
    return(output_text)

def cleanup(input_text):
    return(camelCase(removeSpecialChars(input_text)))


def read_fmm(file):
    # CSV records; rec[0] = FM Keyword; rec[1] = list of FM Dependencies
    # Modify to clean up keywords if needed.
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                feature_id = addRecord(cur, row)
                dependencies = row[4].split(';')  # semi-colon separated list of dependencies in row[4]
                for dependency in dependencies:
                    addDependency(cur, cleanup(dependency), feature_id)
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
tab_rows = getTabs(cur)
for tab_row in tab_rows:
    featureLevel = 0
    parentID = 0
    rootID = 0
    keywordName = tab_row[0]
    keyword = cleanup(keywordName)
    keyWordType = 'MAN'
    tab_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
    updateRootID(cur, tab_feature_id, tab_feature_id)

    # Get list of all functions and create features linked to tabs (keywordName of tab)
    function_rows = getFunctions(cur, keywordName)
    for function_row in function_rows:
        featureLevel = 1
        parentID = tab_feature_id
        rootID = tab_feature_id
        keywordName = function_row[0]
        keyword = cleanup(keywordName)
        keyWordType = 'MAN'
        function_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)

        # Get list of all keywords and create features linked to functions (keywordName of function)
        feature_rows = getFeatures(cur, keywordName)
        for feature_row in feature_rows:
            featureLevel = 2
            parentID = function_feature_id
            rootID = tab_feature_id
            keywordName = feature_row[0]
            keyword = cleanup(keywordName)
            keyWordType = 'MAN'
            feature_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
con.commit()

# Create new "tab" for Common features
featureLevel = 0
parentID = 0
rootID = 0
keywordName = "Common Features"
keyword = cleanup(keywordName)
keyWordType = 'MAN'
common_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
updateRootID(cur, common_feature_id, common_feature_id)
con.commit()

# Create new "functions" for Common features
dep_rows = getDeps(cur)
for dep_row in dep_rows:
    dependency = dep_row[0]
    if dependency.find("Common") == 0:
        featureLevel = 1
        parentID = common_feature_id
        rootID = common_feature_id
        keywordName = dependency
        keyword = cleanup(keywordName)
        keyWordType = 'MAN'
        dep_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
con.commit()

# Create new "features" for any other dependencies missed (should not be any except n/a)
dep_rows = getDeps(cur)
key_rows = getKeywords(cur)
for dep_row in dep_rows:
    keywordName = dep_row[0]
    keyword = cleanup(keywordName)
    if keyword not in key_rows:
        featureLevel = 0
        parentID = 0
        rootID = 0
        keyWordType = 'MAN'
        dep_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
        updateRootID(cur, dep_feature_id, dep_feature_id)
con.commit()


## <<<<<<<<<<<<<<<<< PICKUP HERE.  Need to make sure dependencies are linked and all records are linked to
##  Each other.



# For all dependencies, if the root of the dependency is different than root of its keyword,
#   then add the dependency to the keywords Requires list



#
# allKeywordRows = getKeywordsData(cur)
# for keywordRow in allKeywordRows:
#     keywordID = keywordRow[0]
#     keyword = keywordRow[4]
#     requiresRows = getRequiresFromKeywordID(cur, keywordID)
#     for requiresRow in requiresRows:
#         print(keywordID, requiresRow)
#     # if getKeywordRootIDfromID(keywordID) == getKeywordRootIDfromID(dependencyID):
#     #     updateKeywordParent(keywordID, dependencyID)
#     # else:
#     #     addRequires(dependencyID, keywordID)
# con.commit()





















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

# Loop through all keywords and requires. If a require has same root, make the require
#   be the paraent of the current keyword, ane remove from requires for that keyword.


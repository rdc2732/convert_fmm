# Project to create a new Feature Model out of the FMM

# Approach:
#   1) Parse FMM.txt which contains tab separated file of keywords
#   2) Build list of keywords using FMM GUI items as psuedo-features
#   3) Link all keywords (psuedo and real) with feature type
#   4) Output a new FMM.txt file that can be read with the GUI

import sqlite3
import csv
import re
from convert_fmm_sql2 import *

sqldbfile = 'FMM1.db'
csvfile = 'FMM.txt'     # Using csv reader for tab separated file
csvfileout = 'FMMout.txt' # Using csv writer for tab separated file

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

# 'FM Selection (GUI)', 'Function (GUI)', 'Selectable Options (GUI)', 'FM Selection',
#     'FM Selection Dependencies', 'Rule Type', 'Selection Min', 'Selection Max'
def read_fmm(file):
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                # level, parent_id, root_id, keyword, keyword_name, keyword_type, min, max
                rule_type = 'MAN'
                min = 1
                max = 1
                level = 0
                tab_name = row[0]
                tab = 't_' + cleanup(tab_name)
                tab_id = getKeywordID(cur, tab)
                if tab_id == None:
                    tab_id = addKeyword(cur, level, None, None, tab, tab_name, rule_type, min, max)
                    updateRootID(cur, tab_id, tab_id)
                    con.commit()

                level = 1
                function_name = row[1]
                function = 'f_' + cleanup(function_name)
                function_id = getKeywordID(cur, function)
                if function_id == None:
                    function_id = addKeyword(cur, level, tab_id, tab_id, function, function_name, rule_type, min, max)
                    con.commit()

                level = 2
                feature_name = row[2]
                feature = cleanup(row[3])
                rule_type = row[5]
                if rule_type == 'Selection':
                    rule_type = 'OPT'
                if rule_type == 'Choice':
                    rule_type = 'ALT'
                if rule_type == 'Option':
                    rule_type = 'OR'
                min = row[6]
                max = row[7]
                feature_id = getKeywordID(cur, feature)
                if feature_id == None:
                    feature_id = addKeyword(cur, level, function_id, tab_id, feature, feature_name, rule_type,  min, max)
                    con.commit()
                else:
                    print("Add feature error", feature)




# <<<<<<<<<<<<<<<< PICK UP HERE:  Handle dependencies and correctly handle Rule Types >>>>>>>>>>>>

                dependencies = row[4]
                dependencies = row[4].split(';')  # semi-colon separated list of dependencies in row[4]
                # for dependency in dependencies:
                #     addDependency(cur, cleanup(dependency), feature_id)
            line_count += 1
        print(f'Processed {line_count} lines.')

def write_fmm(file, row_data):
    with open(file) as csv_file:
        csv_writer = csv.writer(csv_file, delimter='\t')
        csv_writer.writerows(row_data)

    csv_writer.close()


##### main program #####

# Set up sqlite database
con = sqlite3.connect(sqldbfile)
cur = con.cursor()
drop_tables(cur)
create_tables(cur)

# Load database with records from FMM.txt
read_fmm(csvfile)









##===================================================================

# # Get list of all tabs and create features
# tab_rows = getTabs(cur)
# for tab_row in tab_rows:
#     featureLevel = 0
#     parentID = 0
#     rootID = 0
#     keywordName = tab_row[0]
#     keyword = cleanup(keywordName)
#     keyWordType = 'MAN'
#     tab_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
#     updateRootID(cur, tab_feature_id, tab_feature_id)
#
#     # Get list of all functions and create features linked to tabs (keywordName of tab)
#     function_rows = getFunctions(cur, keywordName)
#     for function_row in function_rows:
#         featureLevel = 1
#         parentID = tab_feature_id
#         rootID = tab_feature_id
#         keywordName = function_row[0]
#         keyword = cleanup(keywordName)
#         keyWordType = 'MAN'
#         function_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
#
#         # Get list of all keywords and create features linked to functions (keywordName of function)
#         feature_rows = getFeatures(cur, keywordName)
#         for feature_row in feature_rows:
#             featureLevel = 2
#             parentID = function_feature_id
#             rootID = tab_feature_id
#             keywordName = feature_row[0]
#             keyword = cleanup(keywordName)
#             keyWordType = 'MAN'
#             feature_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
# con.commit()
#
# # Create new "tab" for Common features
# featureLevel = 0
# parentID = 0
# rootID = 0
# keywordName = "Common Features"
# keyword = cleanup(keywordName)
# keyWordType = 'MAN'
# common_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType, min, max)
# updateRootID(cur, common_feature_id, common_feature_id)
# con.commit()
#
# # Create new "functions" for Common features
# dep_rows = getDeps(cur)
# for dep_row in dep_rows:
#     dependency = dep_row[0]
#     if dependency.find("Common") == 0:
#         featureLevel = 1
#         parentID = common_feature_id
#         rootID = common_feature_id
#         keywordName = dependency
#         keyword = cleanup(keywordName)
#         keyWordType = 'MAN'
#         dep_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType, min, max)
# con.commit()
#
# # Create new "features" for any other dependencies missed (should not be any except n/a)
# dep_rows = getDeps(cur)
# key_rows = getKeywords(cur)
# for dep_row in dep_rows:
#     keywordName = dep_row[0]
#     keyword = cleanup(keywordName)
#     if keyword not in key_rows:
#         featureLevel = 0
#         parentID = 0
#         rootID = 0
#         keyWordType = 'MAN'
#         dep_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
#         updateRootID(cur, dep_feature_id, dep_feature_id)
# con.commit()
#
# # Create new "features" for any other keywords from records missed
# rec_rows = getAllRecords(cur)
# for rec_row in rec_rows:
#     keywordName = rec_row[5]
#     keyword = cleanup(keywordName)
#
#     if keyword not in key_rows:
#         featureLevel = 0
#         parentID = 0
#         rootID = 0
#         keyWordType = 'MAN'
#         dep_feature_id = addKeyword(cur, featureLevel, parentID, rootID, keyword, keywordName, keyWordType)
#         updateRootID(cur, dep_feature_id, dep_feature_id)
# con.commit()
#
# # For each keyword in records: if dependency has same root, set keyword parent equal to dependency,
# #    else add dependency to keywords requires
# rec_dep_rows = getAllRecordsAndDependencies(cur)
# for rec_dep_row in rec_dep_rows:
#     keywordName = rec_dep_row[5]
#     keywordID = getKeywordID(cur, keywordName)
#     keyword_root_id = getKeywordRootID(cur, keywordName)
#
#     dependencyName = rec_dep_row[11]
#     dependencyID = getKeywordID(cur, dependencyName)
#     dependency_root_id = getKeywordRootID(cur, dependencyName)
#
#     if keyword_root_id == dependency_root_id:
#         updateKeywordParent(cur, keywordID, dependencyID)
#         print("update", keywordID, dependencyID)
#     else:
#         addRequires(cur, keywordID, dependencyID)
#         print("addreq", keywordID, dependencyID)
#
#
# con.commit()
#
# # Write sample FMM.txt file
# rec_req_rows = getKeywordsData(cur)
# row_buffer = [("FM Selection (GUI)","Function (GUI)","Selectable Options (GUI)",\
#                "FM Selection","FM Selection Dependencies","Rule Type","Selection Min","Selection Max")]
# for rec_req_row in rec_req_rows:
#     tab = ""
#     function = ""
#     featureName = ""
#     feature = ""
#     dependencies = ""
#     rule_type = ""
#     min = None
#     max = None
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#     # keyword = record_row[5]
#     # print('\n', keyword)
#     # dependent_rows = getDependents(keyword)
#     # for dependent_row in dependent_rows:
#     #     dependent = dependent_row[2]
#     #     print('\t', dependent)
#         # dependentRootID = getKeywordID(dependent)
#         # parentID = dependent_row[3]
#         # print(dependent, dependentRootID)
#         #
#         # parentRootID = getKeywordRootIDfromID(parentID)
#         # print(parentRootID)
#
#
# # Process all Type I ORs
# # Get list of all Type I
# # For each Type I, create new keywords for each input
# # cur.execute(db_select_OR_keywords_I)
# # for row in cur:
# #     for count in range(row[0]):
# #         new_keyword = row[3] + "_" + str(count)
# #         print(row[1], row[2], row[3], new_keyword)
#
# # Loop through all keywords and requires. If a require has same root, make the require
# #   be the paraent of the current keyword, ane remove from requires for that keyword.
#

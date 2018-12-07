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
    depDict = {} # dictionary to hold list of dependencies for each feature

    # Create new "tab" for Common features
    # level, parent_id, root_id, keyword, keyword_name, keyword_type, min, max
    rule_type = 'MAN'
    min = 1
    max = 1
    level = 0
    common_name = "Common Features"
    common_tab = 't_' + cleanup(common_name)
    common_tab_id = addKeyword(cur, level, None, None, common_tab, common_name, rule_type, min, max)
    updateRootID(cur, common_tab_id, common_tab_id)
    con.commit()

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

                dependencies = row[4].split(';')  # semi-colon separated list of dependencies in row[4]
                depDict.update({feature: dependencies})
            line_count += 1
        print(f'Processed {line_count} lines.')

        # Create new "functions" for Common features
        featureLevel = 1
        parentID = common_tab_id
        rootID = common_tab_id
        rule_type = 'MAN'
        min = 1
        max = 1
        for dependencies in depDict.values():
            for common_function_name in dependencies:
                common_function = 'f_' + cleanup(common_function_name)
                if common_function.find("f_common") == 0:
                    common_function_id = getKeywordID(cur, common_function)
                    if common_function_id == None:
                        common_function_id = addKeyword(cur, featureLevel, parentID, rootID,\
                                common_function, common_function_name, rule_type, min, max)
        con.commit()

        for key in depDict.keys():
            feature = key
            feature_id = getKeywordID(cur, feature)
            feature_root_id = getKeywordRootID(cur, feature)
            feature_parent_data = getKeywordParentIDLevel(cur, feature)
            if feature_parent_data == None:
                continue
            feature_parent_id = feature_parent_data[0]
            feature_level = feature_parent_data[1]
            dependencies = depDict[key]
            for dependency in dependencies:
                dependency_id = getKeywordID(cur, dependency)
                dependency_root_id = getKeywordRootID(cur, dependency)
                dependent_parent_data = getKeywordParentIDLevel(cur, dependency)
                if dependent_parent_data == None:
                    continue
                dependency_parent_id = dependent_parent_data[0]
                dependency_level = dependent_parent_data[1]
                if feature_root_id == dependency_root_id:
                    new_level = dependency_level + 1
                    updateParentIDLevel(cur, feature_id, dependency_id, new_level)
        con.commit()

# Write new FMM.txt file

def write_fmm(file):
    output_rows = []
    csv.register_dialect('myDialect', delimiter='\t', lineterminator = '\n')
    with open(file, 'w') as csv_file:
        tab_rows = getRootKeywordsData(cur)
        for tab_row in tab_rows:
            tab_id = tab_row[0]
            tab_name = tab_row[5]
            function_rows = getKeywordChildrenfromID(cur, tab_id)
            for function_row in function_rows:
                function_name = function_row[4]
                function_keyword = function_row[3]
                function_id = getKeywordID(cur, function_keyword)
                feature_rows = getKeywordChildrenfromID(cur, function_id)
                for feature_row in feature_rows:
                    feature_name = feature_row[4]
                    feature = feature_row[3]
                    feature_type = feature_row[5]
                    feature_min = feature_row[6]
                    feature_max = feature_row[7]
                    output_rows.append([tab_name, function_name, feature_name, feature,\
                            feature_type, feature_min, feature_max])
        csv_writer = csv.writer(csv_file, dialect='myDialect')
        csv_writer.writerows(output_rows)



# def write_fmm(file):
#     csv.register_dialect('myDialect', delimiter='\t', lineterminator = '\n')
#     keyword_rows = getKeywordRelatedData(cur)
#     with open(file, 'w') as csv_file:
#         csv_writer = csv.writer(csv_file, dialect='myDialect')
#         csv_writer.writerows(keyword_rows)






##### main program #####

# Set up sqlite database
con = sqlite3.connect(sqldbfile)
cur = con.cursor()
drop_tables(cur)
create_tables(cur)

# Load database with records from FMM.txt
read_fmm(csvfile)

write_fmm(csvfileout)

# sqlite> .once -x
# sqlite> select distinct k1.keyword_name as tab, k2.keyword_name as function, k3.keyword_name as feature_name, k3.keyword as feature from keywords as k1 join keywords as k2 join keywords as k3 where k3.parent_id = k2.id and k2.parent_id = k1.id;
# Project to create a new Feature Model out of the FMM

# Approach:
#   1) Parse FMM.txt which contains tab separated file of keywords
#   2) Build list of keywords using FMM GUI items as psuedo-features
#   3) Link all keywords (psuedo and real) with feature type
#   4) Output a new FMM.txt file that can be read with the GUI

import csv
import re

csvfile = 'FMM.txt'     # Using csv reader for tab separated file
csvfileout = 'FMMout4.txt' # Using csv writer for tab separated file

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


def get_option(old_option):
    choices = {'MAN': 'Selection', 'Selection': 'MAN', \
               'OPT': 'Option', 'Option': 'OPT', \
               'ALT': 'Choice', 'Choice': 'ALT'}
    new_option = choices[old_option]
    return(new_option)


def read_fmm(file):
    # read CSV file, cleanup keywords, choice and dependencies; save in records table.
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        record_list = list(csv_reader)
        print(f'Read {len(record_list)} lines.')

        # Clean data in the rows.  Collect dictionary of (tab, function, keyword) to
        #   process as OPT records.
        for row in record_list[1:]:
            row[3] = cleanup(row[3])
            row[5] = get_option(row[5])
            new_dependencies = []
            for dependency in row[4].split(';'):
                new_dependencies.append(cleanup(dependency))
            row[4] = ';'.join(new_dependencies)
    return record_list


def write_fmm(file, data):
    header_row = [("FM Selection (GUI)", "Function (GUI)", "Selectable Options (GUI)", \
            "FM Selection", "FM Selection Dependencies", "Rule Type", "Selection Min", \
                  "Selection Max","Description")]
    csv.register_dialect('myDialect', delimiter='\t', lineterminator = '\n')
    with open(file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, dialect='myDialect')
        csv_writer.writerows(header_row)
        csv_writer.writerows(data)


def get_opt_rows(records):
    # Returns a dictionary of options {(tab, function, keyword) : [records]}
    lookup_dict = {}
    for index, row in enumerate(records):
        if index > 0:
            tab = row[0]
            function = row[1]
            keyword = row[3]
            option = (tab, function, keyword)
            if option in lookup_dict:
                row_list = lookup_dict[option]
                row_list.append(index)
                lookup_dict[option] = row_list
            else:
                lookup_dict[option] = [index]
    return lookup_dict


def get_keywords(records):
    # Returns a dictionary of options {(keyword) : [records]} if not in option_dict
    lookup_dict = {}
    for index, row in enumerate(records):
        if index > 0:
            keyword = row[3]
            if keyword in lookup_dict:
                row_list = lookup_dict[keyword]
                row_list.append(index)
                lookup_dict[keyword] = row_list
            else:
                lookup_dict[keyword] = [index]
    return lookup_dict


# Load database with records from FMM.txt
old_fmm_records = read_fmm(csvfile) # Reads text file and creates records and dependencies tables.
new_fmm_records = []
option_dict = get_opt_rows(old_fmm_records)
keyword_dict = get_keywords(old_fmm_records)
dependency_dict = {} # (keyword (from dependency): (tab, function, keyword)}

print("Length of new_fmm_records = ", len(new_fmm_records))

# Process OPT records (where there are multiple records of (tab, function, keyword) tuples
for option in option_dict: # list of all {option tuples: [list of records])
    option_list = option_dict[option]
    if len(option_list) > 1: # options with more than one record
        new_option_rec_id = option_list[0] # First record in list.  The only difference should be in dependencies.
        new_option_record = [*old_fmm_records[new_option_rec_id]] # unpack into new record
        new_option_keyword = new_option_record[3] # Save keyword to be new dependency for option records
        new_option_dependency = new_option_record[4] # Save dependency to lookup record, assumes only one
        new_option_dependency_list = [] # reset list of dependencies
        new_option_record[5] = 'OPT' # ensure option type record for new option record

        for option_rec_id in option_list: # Process each of the OPT records to get dependency info
            option_record = [*old_fmm_records[option_rec_id]] # unpack original option record
            option_keyword = option_record[3]
            option_dependency_list = option_record[4].split(';')
            for option_dependency in option_dependency_list:
                option_dependency_id = keyword_dict[option_dependency][0]
                dependency_record = [*old_fmm_records[option_dependency_id]] # unpack original dependency record
                dependency_keyword = dependency_record[3]
                dependency_dependency = dependency_record[4]
                dependency_record[4] = option_keyword # update record for new dependency
                dependency_record[5] = 'OPT' # ensure option type record for new dependency
                if dependency_dependency not in new_option_dependency_list:
                    new_option_dependency_list.append(dependency_dependency)
                new_fmm_records.append(dependency_record) # save new version of record

        new_option_record[4] = ';'.join(new_option_dependency_list) # update option with new dependency list
        new_fmm_records.append(new_option_record)  # save new version of record

print("Length of new_fmm_records = ", len(new_fmm_records))

# # Process all non-OPT records
# for keyword in keyword_dict: # list of all keywords
#     keyword_list = keyword_dict[keyword]
#     if len(keyword_list) == 1: # keywords with only one record.  Assume all others were processed as OPTs
#         new_keyword_rec_id = keyword_list[0] # First record in list (of only one item)
#
#         new_keyword_record = [*old_fmm_records[new_keyword_rec_id]] # unpack into new record
#         tab = new_keyword_record[0]
#         function = new_keyword_record[1]
#         keyword = new_keyword_record[3]
#         option_index = (tab, function, keyword)
#         if len(option_dict[option_index]):
#             new_fmm_records.append(old_fmm_records[new_keyword_rec_id])  # save new version of record
#         else:
#             print(option_index, len(option_dict[option_index]))

print("Length of new_fmm_records = ", len(new_fmm_records))

# # Create psuedo keywords to represent common tabs and functions
# new_keywords = []
# for keyword in keyword_dict:  # list of all keywords
#     keyword_list = keyword_dict[keyword]
#     keyword_rec_id = keyword_list[0]  # First record in list (of only one item)
#     keyword_record = [*old_fmm_records[keyword_rec_id]] # unpack into new record
#     keyword_dependency_list = keyword_record[4].split(';')
#     for dependency in keyword_dependency_list:
#         if dependency not in keyword_dict and dependency not in new_keywords:
#             new_keywords.append(dependency)
#
# for new_keyword in new_keywords:
#     if new_keyword not in keyword_dict and new_keyword not in ['na']:
#         tab = 'Common Features'     # 0
#         function = new_keyword      # 1
#         if function.find('common-') == 0:
#             function = function[len('common-'):]
#         keyword_name = function     # 2
#         keyword = new_keyword       # 3
#         dependency = 'na'           # 4
#         rule_type = 'MAN'           # 5
#         min = 1                     # 6
#         max = 1                     # 7
#         description = ''            # 8
#         new_data = (tab, function, keyword_name, keyword, dependency, rule_type, min, max, description)
#         new_fmm_records.append(new_data)

print("Length of new_fmm_records = ", len(new_fmm_records))

write_fmm(csvfileout, new_fmm_records)

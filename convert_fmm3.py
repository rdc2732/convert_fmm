# Project to create a new Feature Model out of the FMM

# Approach:
#   1) Parse FMM.txt which contains tab separated file of keywords
#   2) Build list of keywords using FMM GUI items as psuedo-features
#   3) Link all keywords (psuedo and real) with feature type
#   4) Output a new FMM.txt file that can be read with the GUI

import sqlite3
import csv
import re
from convert_fmm_sql3 import *

sqldbfile = 'FMM3.db'
csvfile = 'FMM.txt'     # Using csv reader for tab separated file
csvfileout = 'FMMout3.txt' # Using csv writer for tab separated file

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

choices = {'MAN': 'Selection', 'Selection': 'MAN', \
           'OPT': 'Option', 'Option' : 'OPT', \
           'ALT': 'Choice', 'Choice':'ALT' }

def get_option(old_option):
    new_option = choices[old_option]
    return(new_option)

def read_fmm(file):
    # read CSV file, cleanup keywords, choice and dependencies; save in records table.
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        lines = list(csv_reader)
        print(f'Read {len(lines)} lines.')

        # Clean data in the rows.  Collect dictionary of (tab, function, keyword) to
        #   process as OPT records.
        option_records = {}
        for row in lines[1:]:
            row[3] = cleanup(row[3])
            row[5] = choices[row[5]]
            new_dependencies = []
            for dependency in row[4].split(';'):
                new_dependencies.append(cleanup(dependency))
            row[4] = ';'.join(new_dependencies)
            tab = row[0]
            function = row[1]
            keyword = row[3]
            option = (tab, function, keyword)
            if option in option_records:
                option_count = option_records[option]
                option_records[option] = option_count + 1
            else:
                option_records[option] = 1

            feature_id = addRecord(cur, row)

        for key in option_records:
            if option_records[key] > 1:
                print(key, option_records[key])

        con.commit()


##### main program #####

# Set up sqlite database
con = sqlite3.connect(sqldbfile)
cur = con.cursor()
drop_tables(cur)
create_tables(cur)

# Load database with records from FMM.txt
read_fmm(csvfile) # Reads text file and creates records and dependencies tables.





# write_fmm(csvfileout)


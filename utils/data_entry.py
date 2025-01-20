#data_entry.py
import csv

def read_accounts(filepath='accounting_config/accounts.csv'):
    with open(filepath, 'r') as file:
        accounts = list(csv.reader(file))[1:]
        return accounts
def read_classes(filepath='accounting_config/classes.csv'):
    with open(filepath, 'r') as file:
        classes = list(csv.reader(file))[1:]
        return classes
def read_vendors(filepath='ledger.csv'):
    with open(filepath, 'r') as file:
        csv_reader = csv.DictReader(file)
        vendors = [row['vendor'] for row in csv_reader]
        return vendors
def read_projects(filepath='accounting_config/projects.txt'):
    with open(filepath, 'r') as file:
        projects = [line.strip('\n') for line in file.readlines()]
        return projects

import prompt_toolkit
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder

def fuzzy_autocomplete_prompt(field, strings_for_autocomplete):
    class FuzzyCompleter(Completer):
        def get_completions(self, document, complete_event):
            # Get the entire line up to the cursor
            line_before_cursor = document.current_line_before_cursor
            # Find matches using fuzzyfinder
            matches = fuzzyfinder(line_before_cursor, strings_for_autocomplete)
            # Yield Completion items for each match, replacing the entire line
            for m in matches:
                # -len(line_before_cursor) will replace the whole line before the cursor
                yield Completion(m, start_position=-len(line_before_cursor))
    user_input = prompt_toolkit.prompt(f'Enter {field}: ', completer=FuzzyCompleter())
    return user_input


def receipt_id_generator(description,date_str,master_path):
    words = description.split()
    first_letters = [x[0] for x in words]
    acronym = ''.join(first_letters)
    if len(acronym) > 6:
        acronym = acronym[0:6]
        
    #Read the last line of the master file
    #Modify this so that it works even if the file is empty
    with open(master_path,'r') as master_file:
        transactions = master_file.readlines()
        same_date_transactions = [t.strip('\n') for t in transactions if t[0:10] == date_str]
        numeral = '{:02d}'.format(len(same_date_transactions)+1)
                
    final_string = f'{date_str}-n{numeral}-{acronym}'
    
    return final_string
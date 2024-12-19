#data_entry.py
import csv

def read_accounts(filepath='accounts.csv'):
    with open(filepath, 'r') as file:
        accounts = list(csv.reader(file))[1:]
        return [f'{account_number} {full_name}' for [account_number,full_name,account_type,account_subtype,description] in accounts]
    
def read_classes(filepath='classes.csv'):
    with open(filepath, 'r') as file:
        classes = list(csv.reader(file))[1:]
        return [f'{class_number} {class_name}' for [class_number,class_name] in classes]

import prompt_toolkit
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder

def fuzzy_autocomplete_prompt(field, strings):
    class FuzzyCompleter(Completer):
        def get_completions(self, document, complete_event):
            # Get the entire line up to the cursor
            line_before_cursor = document.current_line_before_cursor

            # Find matches using fuzzyfinder
            matches = fuzzyfinder(line_before_cursor, strings)

            # Yield Completion items for each match, replacing the entire line
            for m in matches:
                # -len(line_before_cursor) will replace the whole line before the cursor
                yield Completion(m, start_position=-len(line_before_cursor))

    user_input = prompt_toolkit.prompt(f'Enter {field}: ', completer=FuzzyCompleter())
    return user_input
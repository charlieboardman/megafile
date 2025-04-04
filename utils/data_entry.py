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
        vendors = list({row['vendor'] for row in csv_reader if row['vendor']})
        return vendors
def read_projects(filepath='accounting_config/projects.txt'):
    with open(filepath, 'r') as file:
        projects = [line.strip('\n') for line in file.readlines()]
        return projects
def read_payment_sources(filepath='accounting_config/payment_sources.txt'):
    with open(filepath, 'r') as file:
        payment_sources = [line.strip('\n') for line in file.readlines()]
        return payment_sources

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
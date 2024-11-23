#data_entry.py

from dateutil import parser
import cv2
import uuid
import questionary
from fuzzywuzzy import process
from datetime import date
import csv

import prompt_toolkit
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder

import img2pdf
import io
from PIL import Image

import os

def read_accounts(filepath='accounts.csv'):
    with open(filepath, 'r') as file:
        accounts = list(csv.reader(file))[1:]
        return [f'{code} {name}' for [code,name] in accounts]
    
def read_classes(filepath='classes.csv'):
    with open(filepath, 'r') as file:
        classes = list(csv.reader(file))[1:]
        return [f'{code} {name}' for [code,name] in classes]
    
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

    
def find_closest_accounts(user_input, accounts, limit=5):
    # Combine the account code and name for each account for the search
    combined_accounts = [f"{code} {name}" for code, name in accounts]
    
    # Find the closest matches to the user_input
    closest_matches = process.extract(user_input, combined_accounts, limit=limit)
    
    # Retrieve the full account information (code and name) for each match
    return [account for match in closest_matches for account in accounts if f"{account[0]} {account[1]}" == match[0]]

def find_closest_classes(user_input, classes, limit=5):
    # Combine the _class code and name for each _class for the search
    combined_classes = [f"{code} {name}" for code, name in classes]
    
    # Find the closest matches to the user_input
    closest_matches = process.extract(user_input, combined_classes, limit=limit)
    
    # Retrieve the full class information (code and name) for each match
    return [_class for match in closest_matches for _class in classes if f"{_class[0]} {_class[1]}" == match[0]]

def select_account():
    accounts = read_accounts()
    while True:
        user_input = input("Start typing an account code or name: ")
        matching_accounts = find_closest_accounts(user_input, accounts)
        
        if not matching_accounts:
            print("No matches found. Please try again.")
            continue
        
        question = [{
            'type': 'list',
            'name': 'choice',
            'message': 'Select account:',
            'choices': [f"{code} - {name}" for code, name in matching_accounts]
        }]
        
        selected = questionary.prompt(question)['choice']
        selected_code, selected_name = selected.split(" - ", 1)
        
        return selected_code, selected_name

def select_class():
    accounts = read_classes()
    while True:
        user_input = input("Start typing a class code or name: ")
        matching_classes = find_closest_classes(user_input, classes)
        
        if not matching_classes:
            print("No matches found. Please try again.")
            continue
        
        question = [{
            'type': 'list',
            'name': 'choice',
            'message': 'Select class:',
            'choices': [f"{code} - {name}" for code, name in matching_classes]
        }]
        
        selected = questionary.prompt(question)['choice']
        selected_code, selected_name = selected.split(" - ", 1)
        
        return selected_code, selected_name

def select_project():
    with open('projects.txt', 'r') as projects_file:
        
        projects = [project.strip('\n') for project in projects_file.readlines() if not project.startswith('#')]
        
        question = [
            {
                'type': 'list',
                'name': 'choice',
                'message': 'Select project:',
                'choices': projects
                }
            ]
        
        project = questionary.prompt(question)
        
        return project['choice']

def receipt_id_generator(description,transaction_date,master_path):
    words = description.split()
    first_letters = [x[0] for x in words]
    acronym = ''.join(first_letters)
    if len(acronym) > 6:
        acronym = acronym[0:8]
        
    #Parse the date
    if isinstance(transaction_date,date):
        date_str = transaction_date.strftime('%Y-%m-%d')
        
    elif type(transaction_date) == str:
        date_str = parser.parse(transaction_date).strftime('%Y-%m-%d')
        
    else:
        print("Bad date format")
        return(0)
    
    
    #Read the last line of the master file
    #Modify this so that it works even if the file is empty
    with open(master_path,'r') as master_file:
        transactions = master_file.readlines()
        same_date_transactions = [t.strip('\n') for t in transactions if t[0:10] == date_str]
        numeral = '{:02d}'.format(len(same_date_transactions)+1)
                
    final_string = f'{date_str}-{acronym}-{numeral}'
    
    return final_string
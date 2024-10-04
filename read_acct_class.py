import csv

def read_accounts(filepath='accounts.csv'):
    with open(filepath, 'r') as file:
        accounts = list(csv.reader(file))[1:]
        return [[code,name] for [code,name] in accounts]
    
def read_classes(filepath='classes.csv'):
    with open(filepath, 'r') as file:
        classes = list(csv.reader(file))[1:]
        return [[code,name] for [code,name] in classes]
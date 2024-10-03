import dateparser
from fuzzy_autocomplete_prompt import fuzzy_autocomplete_prompt
import csv

def spend():
    date_str = dateparser.parse(input('Date: ')).date().isoformat()
    mxn = input('MXN: ')
    usd = input('USD: ')
    vendors = set()
    with open('ledger.csv','r') as ledger_file:
        ledger = csv.reader(ledger_file)
        for row in ledger:
            if row[0] != 'Date':
                vendors.add(row[9])
    vendor = fuzzy_autocomplete_prompt('vendor',vendors)
    
    return date_str,mxn,usd,vendor
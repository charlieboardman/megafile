import dateparser
from fuzzy_autocomplete_prompt import fuzzy_autocomplete_prompt
import csv
import read_acct_class

def spend():
    date_str = dateparser.parse(input('Date: ')).date().isoformat()
    
    _type = 'spend'
    
    accts = [[code,name] for [code,name] in read_acct_class.read_accounts()]
    classes = [[code,name] for [code,name] in read_acct_class.read_classes()]

    accts_combined = [f'{code} {name}' for [code,name] in accts]
    classes_combined = [f'{code} {name}' for [code,name] in classes]

    acct_selected = fuzzy_autocomplete_prompt('Account: ', accts_combined)
    class_selected = fuzzy_autocomplete_prompt('Class: ', classes_combined)

    acct_index = accts_combined.index(acct_selected)
    class_index = classes_combined.index(class_selected)

    acct_code = accts[acct_index][0]
    acct_desc = accts[acct_index][1]

    class_code = accts[class_index][0]
    class_desc = accts[class_index][1]
    
    mxn = input('MXN: ')
    mxn_float = float(mxn)
    
    if mxn != '':
        ER = input('Exchange rate (mxn/usd): ')
        ER_float = float(ER)
        ER_rounded = str(round(float(ER),3))
    else:
        ER = ''
    usd = input('USD: ')
    usd_float = float(usd)
    usd = str(round(float(usd),2))
    
    calc_usd = str(round(mxn_float/ER_float + usd_float))
    
    vendors = set()
    with open('ledger.csv','r') as ledger_file:
        ledger = csv.reader(ledger_file)
        for row in ledger:
            if row[0] != 'Date':
                vendors.add(row[9])
    vendor = fuzzy_autocomplete_prompt('vendor',vendors)
    
    desc = input('Description: ')
    
    notes = input('Notes: ')
    
    
 
    return date_str,mxn,usd,vendor,acct_code,acct_desc,class_code,class_desc
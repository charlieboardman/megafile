from capture_image import capture_image
from datetime import date
import data_entry
from dateparser import parse

row = dict()

accounts = data_entry.read_accounts()
accounts_strings_for_autocomplete = [f'{account_number} {full_name}' for [account_number,full_name,account_type,account_subtype,description] in accounts]

classes = data_entry.read_classes()
classes_strings_for_autocomplete = [f'{class_number} {class_name}' for [class_number,class_name] in classes]

row['date'] = parse(input('Date: ')).date().isoformat()

account_ = data_entry.fuzzy_autocomplete_prompt('account',accounts_strings_for_autocomplete)
row['account_code'] = account_.split(' ')[0]
row['account_name'] = ' '.join(account_.split(' ')[1:])

class_ = data_entry.fuzzy_autocomplete_prompt('class',classes_strings_for_autocomplete)
row['class_code'] = class_.split(' ')[0]
row['class_name'] = ' '.join(class_.split(' ')[1:])

mxn = input('mxn: ')
try:
    float(mxn)
    ER = input('ER: ') #todo add error handling/validation for ER
except:
    ER = ''

usd = input('usd: ')
#todo handle this error better
float(usd)

calc_usd = "{:.2f}".format(float(usd)+float(mxn)/float(ER))
#print(calc_usd)

row['mxn'] = mxn; row['ER'] = ER; row['usd'] = usd; row['calc_usd'] = calc_usd

vendors = data_entry.read_vendors()
row['vendor'] = data_entry.fuzzy_autocomplete_prompt('vendor',vendors)
row['description'] = input('Description: ')
row['notes'] = input('Notes: ')
projects = data_entry.read_projects()
row['project'] = data_entry.fuzzy_autocomplete_prompt('project',projects)
print('Please capture receipt')
receipt_pdf = capture_image() #todo need to save this to disk/drive
row['receipt_id'] = data_entry.receipt_id_generator(row['description'],row['date'],'ledger.csv')
#todo need to append the row to the real ledger/google sheet

print(row)

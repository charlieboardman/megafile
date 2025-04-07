from utils.capture_image import capture_image
from datetime import date
import utils.data_entry as data_entry
from utils.calculate_usd import calculate_usd
from dateparser import parse
import os
from dotenv import load_dotenv
from utils.gas_poster import post_data_to_gas
from utils.fiscal_year_calculator import fiscal_year_calculator
import base64

row = dict()

accounts = data_entry.read_accounts()
accounts_strings_for_autocomplete = [f'{account_number} {full_name}' for [account_number,full_name,account_type,account_subtype,description] in accounts]

classes = data_entry.read_classes()
classes_strings_for_autocomplete = [f'{class_number} {class_name}' for [class_number,class_name] in classes]

row['date'] = parse(input('Date: ')).date().isoformat()
row['fiscal_year'] = fiscal_year_calculator(row['date'])

payment_source_strings_for_autocomplete = data_entry.read_payment_sources()
payment_source = data_entry.fuzzy_autocomplete_prompt('payment source (blank for petty cash)',payment_source_strings_for_autocomplete)

if payment_source == '':
    payment_source = 'Petty cash'
row['payment_source'] = payment_source

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

calc_usd = calculate_usd(usd,mxn,ER)
#print(calc_usd)

row['mxn'] = mxn; row['ER'] = ER; row['usd'] = usd; row['calc_usd'] = calc_usd

vendors = data_entry.read_vendors()
row['vendor'] = data_entry.fuzzy_autocomplete_prompt('vendor',vendors)
row['description'] = input('Description: ')
row['notes'] = input('Notes: ')
projects = data_entry.read_projects()
row['project'] = data_entry.fuzzy_autocomplete_prompt('project',projects)

#Capture receipt image and convert to base64 string
print('Please capture receipt')
receipt_pdf = capture_image()
receipt_base64 = base64.b64encode(receipt_pdf).decode('utf-8')

row['accounting_notes'] = '' #Add a blank column for accounting notes

#Get secrets
load_dotenv()
GAS_APP_URL = os.getenv("GAS_APP_URL")
HMAC_SECRET_KEY = os.getenv("HMAC_SECRET_KEY")

#Post the receipt to the web app
result = post_data_to_gas(row, receipt_base64, GAS_APP_URL, HMAC_SECRET_KEY)

print(result)
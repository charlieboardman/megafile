def fiscal_year_calculator(date): #Date as a string in iso format
    calendar_month = int(date[5:7])
    if calendar_month >= 9: #Our fiscal year starts in September. Edit this 9 if other month needed
        return str(int(date[0:4])+1)
    else:
        return date[0:4]
    
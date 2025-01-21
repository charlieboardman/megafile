def calculate_usd(usd,mxn,ER):
    if usd == '':
        usd = float(0)
    else:
        usd = float(usd)
        
    if mxn == '':
        mxn = float(0)
    else:
        mxn = float(mxn)
        
    if ER == '':
        ER = float(1)
    else:
        ER = float(ER)
    
    return "{:.2f}".format(usd+mxn/ER)
#!/usr/bin/env python

import MySQLdb


db = MySQLdb.connect("localhost", "monitor", "password", "coins")
curs=db.cursor()

# note that I'm using triplle quotes for formatting purposes
# you can use one set of double quotes if you put the whole string on one line
currency= "EUR"
#sell_price = CBclient.get_sell_price(currency='EUR')
#buy_price  = CBclient.get_buy_price(currency='EUR')
account = "EUR wallet"
payment_method = "testmethod"
sell_price = 1
buy_price=1
ttype= "test"

with db:
    curs.execute("""INSERT INTO transactions (transaction_ID, ttype, transaction_datetime, amount_from, buy_price, sell_price,currency,payment_method,account) values(0, """+"'"+str(ttype)+"'"+""",CURRENT_TIMESTAMP(),23,12.44,13.55,'EUR','2','4')""")
    
curs.execute ("SELECT * FROM transactions")

print "\nDate         Time        Zone        Temperature"
print "==========================================================="

for reading in curs.fetchall():
    print str(reading[0])+"    "+str(reading[1])+"     "+\
                str(reading[2])+"      "+str(reading[3])
                
db.close()
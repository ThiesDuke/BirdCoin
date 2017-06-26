#!/usr/bin/env python
from coinbase.wallet.client import Client

client = Client(
    "2DUjHD6flVHWNfbY",
    "ZjEP7CdirBgGvx2P6StDNFMIOqj6ymbS")

accounts = client.get_accounts()
#for account in accounts.data:
#  balance = account.balance
#  print "%s: %s %s" % (account.name, balance.amount, balance.currency)
#  print account.get_transactions()
#payment_methods = client.get_payment_methods()
#print payment_methods
account = accounts[2]
payment_method = client.get_payment_methods()[2]
#buy = account.buy(amount='1',
#                    currency="EUR",
#                    payment_method=payment_method.id)
#buy_price  = client.get_buy_price(currency='EUR')
#sell_price = client.get_sell_price(currency='EUR')
#print accounts[0]
#print account
#print payment_method
#print buy_price
#print sell_price

#buy_price_threshold  = 200
#sell_price_threshold = 500

#if float(sell_price.amount) <= sell_price_threshold:
#  sell = account.sell(amount='1',
#                      currency="BTC",
#                      payment_method=payment_method.id)


#if float(buy_price.amount) <= buy_price_threshold:
#  buy = account.buy(amount='1',
#                    currency="BTC",
#                    payment_method=payment_method.id)
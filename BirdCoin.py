#!/usr/bin/env python
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import math
import datetime
import cv2
import MySQLdb
import Humiture
import BMP085 as BMP085
from coinbase.wallet.client import Client
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from base64 import test
import multiprocessing as mp
import logging

logging.basicConfig()        
db_evaluate = MySQLdb.connect("localhost", "monitor", "password", "coins")
db_birds = MySQLdb.connect("localhost", "monitor", "password", "coins")
curs_evaluate=db_evaluate.cursor()
curs_birds=db_birds.cursor()
CBclient = Client(
    "2DUjHD6flVHWNfbY",
    "ZjEP7CdirBgGvx2P6StDNFMIOqj6ymbS")

def get_environmental_data():
    print("get_environmental_data")
    sensor = BMP085.BMP085()
    temp = sensor.read_temperature()    # Read temperature to veriable temp
    pressure = sensor.read_pressure()    # Read pressure to veriable pressure
    humidity = None
    while humidity == None:
        result = Humiture.read_dht11_dat()
        if result:
            humidity= result[0]
    return pressure,temp, humidity

def is_prime(n):
    print("is_prime")
    for i in range(3, n):
        if n % i == 0:
            return False
    return True

def evaluate_action():
    print("evaluate_action")
    global db_evaluate,curs_evaluate
    f = '%Y-%m-%d %H:%M:%S'
    with db_evaluate:
        curs_evaluate.execute("select count(*) from tempdat WHERE tdatetime>CURRENT_TIMESTAMP()-INTERVAL 1 HOUR")
    test_number = curs_evaluate.fetchone()[0]
    print(test_number)
    print(is_prime(test_number))
    if is_prime(test_number):
        with db_evaluate:
            curs_evaluate.execute("select transaction_datetime from transactions ORDER BY transaction_ID DESC LIMIT 1")
        last_transaction_datetime = curs_evaluate.fetchone()[0]
        last_transaction_datetime_1 = last_transaction_datetime.strftime(f)
        with db_evaluate:
            curs_evaluate.execute ("""SELECT AVG(pressure),AVG(temperature),AVG(humidity) FROM tempdat WHERE tdatetime > """+"'"+str(last_transaction_datetime_1)+"'"+"""""")
        average_pressure, average_temperature, average_humidity = curs_evaluate.fetchone()
        current_pressure, current_temperature, current_humidity = get_environmental_data()
        if average_pressure < current_pressure:
            buy_sell_evaluation_0=1
        else:
            buy_sell_evaluation_0=0
        if average_temperature < current_temperature:
            buy_sell_evaluation_1=1
        else:
            buy_sell_evaluation_1=0
        if average_humidity < current_humidity:
            buy_sell_evaluation_2=1
        else:
            buy_sell_evaluation_2=0
        if (buy_sell_evaluation_0+buy_sell_evaluation_1+buy_sell_evaluation_2)>1:
            buy_sell_result = 1
        else:
            buy_sell_result = 0
        with db_evaluate:
            curs_evaluate.execute ("""SELECT COUNT(*) FROM tempdat WHERE tdatetime > """+"'"+str(last_transaction_datetime_1)+"'"+"""""")
        number_of_entries = curs_evaluate.fetchone()[0]
        trade(buy_sell_result,number_of_entries)

def trade(buy_sell_result,number_of_entries):
    print("trade")
    global db_evaluate, curs_evaluate
    global CBclient
    print buy_sell_result
    print number_of_entries
    accounts = CBclient.get_accounts()
    account = accounts[2]
    payment_method = CBclient.get_payment_methods()[2]
    sell_price = CBclient.get_sell_price(currency='EUR')
    buy_price  = CBclient.get_buy_price(currency='EUR')
    if buy_sell_result == 0:
        #sell = account.sell(amount='1',
        #                      currency="EUR",
        #                      payment_method=payment_method.id)
        balance = account.balance
        #balance = 12
        message = "Sold coins: "+str(number_of_entries)+" EUR @" + str(sell_price.amount) + " EUR."
        ttype = "sell"
    if buy_sell_result == 1:
        #buy = account.buy(amount='1',
        #                    currency="EUR",
        #                    payment_method=payment_method.id)
        balance = account.balance
        #balance=13
        message = "Bought coins: "+str(number_of_entries)+" EUR @" + str(buy_price.amount) + " EUR."
        ttype = "buy"
    print(ttype)
    with db_evaluate:
		curs_evaluate.execute("""INSERT INTO transactions (transaction_ID, ttype, transaction_datetime, amount_from, buy_price, sell_price,currency,payment_method,account) values(0, """+"'"+str(ttype)+"'"+""",CURRENT_TIMESTAMP(),"""+"'"+str(number_of_entries)+"'"+""","""+"'"+str(buy_price.amount)+"'"+""","""+"'"+str(sell_price.amount)+"'"+""","""+"'"+str(sell_price.currency)+"'"+""","""+"'"+str(payment_method.name)+"'"+""","""+"'"+str(account.name)+"'"+""")""")
		curs_evaluate.execute("select balance_EUR,balance_BTC from account ORDER BY atransaction_ID DESC LIMIT 1")
		balance_EUR, balance_BTC = curs_evaluate.fetchone()
		if ttype == "buy":
			new_balance_EUR = balance_EUR - float(number_of_entries)
			new_balance_BTC = balance_BTC + float(number_of_entries)/float(buy_price.amount)
		if ttype == "sell":
			new_balance_EUR = balance_EUR + float(number_of_entries)
			new_balance_BTC = balance_BTC - float(number_of_entries)/float(sell_price.amount)
		curs_evaluate.execute("""INSERT INTO account (atransaction_ID, atimestamp, balance_EUR, balance_BTC) values(0,CURRENT_TIMESTAMP(), """+"'"+str(new_balance_EUR)+"'"+""","""+"'"+str(new_balance_BTC)+"'"+""")""")
		total_balance = new_balance_EUR + new_balance_BTC*float(sell_price.amount)
		message = message + " Current EUR balance = "+str(new_balance_EUR)+". New BTC balance = " + str(new_balance_BTC)+ " Total balance =: "+str(round(total_balance,2))+" EUR."
		telegram(message)

def telegram(message):
    print("telegram")
    telegram_message = message
    bottoken = "323438192:AAGs3TXyYuR0Tq9QKjulCP5cVkLaZD3wAc8"
    url = "https://api.telegram.org/bot" + bottoken + "/sendMessage"
    params = { "chat_id": -230308873, "text": telegram_message }
    r = requests.get(url, params=params)
    result = r.json()

def save_bird_visit():
    global db_birds, curs_birds
    print("save_bird_visit")
    THRESHOLD = 50
    MIN_AREA = 100000
    BLURSIZE = (15,15)
    IMAGEWIDTH = 640
    IMAGEHEIGHT = 480
    RESOLUTION = [IMAGEWIDTH,IMAGEHEIGHT]
    FPS = 30

    base_image = None
    camera = PiCamera()
    camera.resolution = RESOLUTION
    camera.framerate = FPS
    camera.vflip = False
    camera.hflip = False
    camera.rotation = 90
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    time.sleep(0.9)

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        timestamp = datetime.datetime.now()
        image = frame.array
        gray = image
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, BLURSIZE, 0)
        if base_image is None:
            base_image = gray.copy().astype("float")
            lastTime = timestamp
            rawCapture.truncate(0)
            #cv2.imshow("Speed Camera", image)
            continue
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(base_image))
        thresh = cv2.threshold(frameDelta, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        motion_found = False
        biggest_area = 0
        for c in cnts:
            motion_found = False
            (x, y, w, h) = cv2.boundingRect(c)
            found_area = w*h 
            if (found_area > MIN_AREA) and (found_area > biggest_area):
                motion_found = True
                print("motion detected")
                cv2.imwrite("bird_at_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".jpg",image)
                pressure, temp, humidity = get_environmental_data()
                with db_birds:
                    curs_birds.execute ("""INSERT INTO tempdat (ID, tdatetime, pressure, temperature, humidity) values(0, CURRENT_TIMESTAMP(), """+ str(pressure) +""", """ + str(temp) + """, """+str(humidity)+""")""")
        rawCapture.truncate(0)
        time.sleep(3)

def destroy():
    print("destroy")
    db_evaluate.close()
    db_birds.close()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    try:
        scheduler = BlockingScheduler()
        scheduler.add_job(evaluate_action, 'interval', minutes=60)
        p_a = mp.Process(target=save_bird_visit)
        p_b= mp.Process(target=scheduler.start)
        p_a.start()
        p_b.start()
        p_a.join()
        p_b.join()
        #save_bird_visit()
        #scheduler.start()
    except KeyboardInterrupt:
        destroy()
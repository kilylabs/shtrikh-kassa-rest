# encoding=utf8
import os,os.path
import string
import time
import sys
from eve import Eve

import kkm_conf
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import kilykkt

app = Eve(settings='lib/rest_conf.py')

def on_inserted_report(items):
    print 'About to store report'
    if items:
        sfrk = kilykkt.KilyKKT(
            password=kkm_conf.PASSWORD,
            admin_password=kkm_conf.ADMIN_PASSWORD,
            port=kkm_conf.PORT,
            bod=kkm_conf.BAUD_RATE,
            parity=kkm_conf.PARITY,
            stopbits=kkm_conf.STOPBITS,
            timeout=kkm_conf.TIMEOUT,
            writeTimeout=kkm_conf.WRITE_TIMEOUT
        )
        for json_data in items:
            if json_data['type'] == 'x':
                sfrk.printSession()
            elif json_data['type'] == 'z':
                sfrk.closeSession()

def on_inserted_checks(items):
    print 'About to store checks'
    if items:
        sfrk = kilykkt.KilyKKT(
            password=kkm_conf.PASSWORD,
            admin_password=kkm_conf.ADMIN_PASSWORD,
            port=kkm_conf.PORT,
            bod=kkm_conf.BAUD_RATE,
            parity=kkm_conf.PARITY,
            stopbits=kkm_conf.STOPBITS,
            timeout=kkm_conf.TIMEOUT,
            writeTimeout=kkm_conf.WRITE_TIMEOUT
        )
        for json_data in items:

	    try: 
	        sfrk.cancelCheck();
            except kilykkt.kkt.KktError,e:
                print "err";
            except TypeError,e2:
                print "err2";

            srq = sfrk.statusRequest()
            if srq['kkt_mode'] == 3:
                sfrk.closeSession();

            if ('type' in json_data):
                types = {
                        'sale':0,
                        'buy':1,
                        'sale_return':2,
                        'buy_return':3
                }
                sfrk.openCheck(types[json_data['type']])
            else:
                sfrk.openCheck(0)

            header = " \n \n"

            if ('barcode' in json_data) and (json_data['barcode']):
                for l in header.split('\n'):
                    sfrk.printString(text=l)
                sfrk.printBarcode(json_data['barcode'])

            for l in header.split('\n'):
                sfrk.printString(text=l)

            sfrk.printString(text=u"Принято от: %s" % json_data["client_name"])
            if ('order_id' in json_data) and (json_data['order_id']):
                sfrk.printString(text=u"По заказу: %s" % json_data["order_id"])

            for l in header.split('\n'):
                sfrk.printString(text=l)

            summ = 0.0
            pays = [0,0,0,0]
            taxes = [0,0,0,0]
            for position in json_data['positions']:
                name = position['art'] + ' ' + position['name']
                name = name[:40]
                summ += position['price'] * position['quantity'];
                sfrk.sale(position['price'],name,position['quantity'],0,taxes)

            subtypes = {
                    'sale':0,
                    'buy':1,
                    'sale_return':2,
                    'buy_return':3
                    }

            if ('subtype' in json_data):
                if json_data['subtype'] == 'card':
                    pays[1] = summ
                elif json_data['subtype'] == 'special1':
                    pays[2] = summ
                elif json_data['subtype'] == 'special2':
                    pays[3] = summ
                else:
                    pays[0] = summ
            else:
                pays[0] = summ

            sfrk.closeCheck(0,pays,0,taxes,text=u"------------------")


app.on_inserted_checks += on_inserted_checks
app.on_inserted_report += on_inserted_report

if __name__ == '__main__':
    app.run(host=kkm_conf.LISTEN_HOST,port=kkm_conf.LISTEN_PORT)

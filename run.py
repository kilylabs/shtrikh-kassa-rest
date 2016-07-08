# encoding=utf8
import os,os.path
import string
import time
from datetime import datetime
import sys
from eve import Eve
import pprint
import logging
from logging.handlers import RotatingFileHandler

import kkm_conf

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = kkm_conf.DEBUG_LEVEL, filename = os.path.join(os.path.dirname(__file__), "log","kkm.log"),backupCount=5)

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import kilykkt

def on_inserted_report(items):
    app.logger.info('About to store report')
    if items:
        app.logger.debug('Report data is: %s',pprint.pformat(items))
        sfrk = kilykkt.KilyKKT(
                logger=app.logger
                )
        for json_data in items:
            if json_data['type'] == 'x':
                sfrk.printSession()
            elif json_data['type'] == 'z':
                sfrk.closeSession()

def on_inserted_checks(items):
    app.logger.info('About to store checks')
    if items:
        app.logger.debug('Check data is: %s',pprint.pformat(items))
        sfrk = kilykkt.KilyKKT(
            logger=app.logger
        )

        sfrk.acquireLock()
        try:
            for json_data in items:
                srq = sfrk.statusRequest()
                app.logger.debug('Status request is: %s',pprint.pformat(srq))
                if srq['kkt_mode'] == 3:
                    sfrk.closeSession();
                elif srq['kkt_mode'] in (8,40):
                    sfrk.cancelCheck();

                types = {
                        'sale':0,
                        'buy':1,
                        'sale_return':2,
                        'buy_return':3
                        }

                if ('type' not in json_data):
                    json_data['type'] = 'sale'

                sfrk.openCheck(types[json_data['type']])

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
                    sfrk.sale(types[json_data['type']],position['price'],name,position['quantity'],0,taxes)

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

        except kilykkt.kkt.KktError,e:
           sfrk.releaseLock()
           raise
        except:
           sfrk.releaseLock()
           raise

        sfrk.releaseLock()

app = Eve(settings='lib/rest_conf.py')
app.on_inserted_checks += on_inserted_checks
app.on_inserted_report += on_inserted_report

if __name__ == '__main__':
    if len(sys.argv) == 1:
        app.logger.info("starting kkm app...")
        app.run(host=kkm_conf.LISTEN_HOST,port=kkm_conf.LISTEN_PORT)
    else:
        sfrk = kilykkt.KilyKKT(
                logger=app.logger
                )
        args = sys.argv[2:]
        print getattr(sfrk, sys.argv[1] )(*args)

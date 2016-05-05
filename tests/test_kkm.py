# encoding=utf8

import pytest 
import os,os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../lib"))

import kkm_conf
import kilykkt

def test_creation():
    sfrk = kilykkt.KilyKKT()

def test_statusRequest():
    sfrk = kilykkt.KilyKKT()

    srq = sfrk.statusRequest()
    assert 'kkt_mode' in srq

def test_printSession():
    sfrk = kilykkt.KilyKKT()

    sfrk.printSession()

def test_closeSession():
    sfrk = kilykkt.KilyKKT()

    sfrk.closeSession()

def test_openCheck():
    sfrk = kilykkt.KilyKKT()
    
    sfrk.openCheck(0)

def test_printString():
    sfrk = kilykkt.KilyKKT()

    sfrk.printString(u"Test line")
    sfrk.printString(u"Тест тест тест 123")

def test_printBarcode():
    sfrk = kilykkt.KilyKKT()

    sfrk.printBarcode(1234567)

def test_sale():
    sfrk = kilykkt.KilyKKT()

    taxes = [0,0,0,0]
    sfrk.sale(100.75,u"Banana",1,0,taxes)
    sfrk.sale(20.05,u"",5,0,taxes)

def test_closeCheck():
    sfrk = kilykkt.KilyKKT()

    pays = [201,0,0,0]
    taxes = [0,0,0,0]
    sfrk.closeCheck(0,pays,0,taxes,text=u"------------------")

def test_cancelCheck():
    sfrk = kilykkt.KilyKKT()

    sfrk.openCheck(0)
    taxes = [0,0,0,0]
    sfrk.sale(100.75,u"Banana",1,0,taxes)
    sfrk.sale(20.05,u"",5,0,taxes)
    sfrk.cancelCheck()

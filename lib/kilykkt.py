# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals
import os,os.path
import string
import time
import sys
import logging
import threading
import pprint

sys.path.append(os.path.join(os.path.dirname(__file__), "shtrihm-fr"))
import kkm_conf
import shtrihmfr
from shtrihmfr import kkt

class KilyKKT(kkt.KKT):

    lock = threading.Lock()
    logger = False
    sale_types = { 
            0:0x80,
            1:0x81,
            2:0x82,
            3:0x83
    }

    """ Класс с основными функциями REST API """

    def __init__(self,**kwargs):
        """ Передаем параметры из конфига родительскому конструктору """

        if 'logger' in kwargs:
            self.logger = kwargs.pop('logger')

        kkt.MAX_ATTEMPT = kkm_conf.MAX_ATTEMPT

        super(kkt.KKT, self).__init__(
                password=kkm_conf.PASSWORD,
                admin_password=kkm_conf.ADMIN_PASSWORD,
                port=kkm_conf.PORT,
                bod=kkm_conf.BAUD_RATE,
                parity=kkm_conf.PARITY,
                stopbits=kkm_conf.STOPBITS,
                timeout=kkm_conf.TIMEOUT,
                writeTimeout=kkm_conf.WRITE_TIMEOUT,
                **kwargs
        )
        self.resetSerial()

    def acquireLock(self):
        self.logger.debug("Aquiring lock...") if self.logger else False
        self.lock.acquire();

    def releaseLock(self):
        self.logger.debug("Releasing lock...") if self.logger else False
        self.lock.release();

    def resetSerial(self):
        self.conn.setDTR(False)
        time.sleep(1)
        self.conn.flushInput()
        self.conn.setDTR(True)
        self.connect()
        self.clear()

    def wrap(self,cmd,*args):
        """ Обработчик для логов, lock-а и на случай ошибок типа 0x50 (принтер занят) """

        self.logger.debug("Calling %s cmd with args: %s",cmd,pprint.pformat(args)) if self.logger else False

        #self.acquireLock()
        while True:
            try:
                ret = getattr(self, cmd )(*args)
            except kkt.KktError,e:
                if hasattr(e,"value") and (0x50 == e.value):
                    continue
                else:
                    #self.releaseLock()
                    raise
            except:
                #self.releaseLock()
                raise
            break

        #self.releaseLock()
        return ret

    def send(self, command, params, quick=False):
        """ Тот же самый метов KKT.send, но с добавление логирования """

        #~ self.clear()

        if not quick:
            self._flush()
        data    = chr(command)
        length  = 1
        if not params is None:
            data   += params
            length += len(params)
        content = chr(length) + data
        control_summ = kkt.get_control_summ(content)

        s = kkt.STX + content + control_summ
        self.logger.debug(":".join("{:02x}".format(ord(c)) for c in s)) if self.logger else False

        self._write(s)
        self._flush()

        return True

    def _read(self, read=None):
        """ Высокоуровневый метод считывания соединения """
        s = self.conn.read(read)
        self.logger.debug("Read: "+":".join("{:02x}".format(ord(c)) for c in s)) if self.logger else False
        return s

    def ask(self, command, params=None, sleep=0, pre_clear=True,\
                without_password=False, disconnect=True, quick=False):
        """ Высокоуровневый метод получения ответа. Состоит из
            последовательной цепочки действий. 
            
            Возвращает позиционные параметры: (data, error, command)
        """

        #~ raise KktError('Тест ошибки')
        if quick:
            pre_clear  = False
            disconnect = False
            sleep      = 0

        if params is None and not without_password:
            params = self.password
        #~ if pre_clear:
            #~ self.clear()
        self.send(command, params, quick=quick)
        if sleep:
            self.logger.debug("Sleeping for %d sec",sleep) if self.logger else False
            time.sleep(sleep)
        a = self.read()
        answer, error, command = (a['data'], a['error'], a['command'])
        if disconnect:
            self.disconnect()
        if error:
            raise kkt.KktError(error)

        return answer, error, command

    def statusRequest(self):
        """ Короткий запрос состояния ФР
            Команда: 10H. Длина сообщения: 5 байт.
                Пароль оператора (4 байта)
            Ответ: 10H. Длина сообщения: 16 байт.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 1...30
                Флаги ККТ (2 байта)
                Режим ККТ (1 байт)
                Подрежим ККТ (1 байт)
                Количество операций в чеке (1 байт) младший байт
                    двухбайтного числа (см. документацию)
                Напряжение резервной батареи (1 байт)
                Напряжение источника питания (1 байт)
                Код ошибки ФП (1 байт)
                Код ошибки ЭКЛЗ (1 байт)
                Количество операций в чеке (1 байт) старший байт
                    двухбайтного числа (см. документацию)
                Зарезервировано (3 байта)
        """
        return self.wrap("x10_enh")

    def printSession(self):
        """ Суточный отчет без гашения
            Команда: 40H. Длина сообщения: 5 байт.
                Пароль администратора или системного администратора (4 байта)
            Ответ: 40H. Длина сообщения: 3 байта.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 29, 30
        """
        return self.wrap("x40");

    def closeSession(self):
        """ Суточный отчет с гашением
            Команда: 41H. Длина сообщения: 5 байт.
                Пароль администратора или системного администратора (4 байта)
            Ответ: 41H. Длина сообщения: 3 байта.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 29, 30
        """
        return self.wrap("x41")

    def openCheck(self, document_type):
        """ Открыть чек
            Команда: 8DH. Длина сообщения: 6 байт.
                Пароль оператора (4 байта)
                Тип документа (1 байт):
                    0 – продажа;
                    1 – покупка;
                    2 – возврат продажи;
                    3 – возврат покупки
            Ответ: 8DH. Длина сообщения: 3 байта.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 1...30
        """
        return self.wrap("x8D",document_type)

    def closeCheck(self, cash=0, summs=[0,0,0,0], discount=0, taxes=[0,0,0,0], text=''):
        """ Закрытие чека
            Команда: 85H. Длина сообщения: 71 байт.
                Пароль оператора (4 байта)
                Сумма наличных      (5 байт) 0000000000...9999999999
                Сумма типа оплаты 2 (5 байт) 0000000000...9999999999
                Сумма типа оплаты 3 (5 байт) 0000000000...9999999999
                Сумма типа оплаты 4 (5 байт) 0000000000...9999999999
                Скидка/Надбавка(в случае отрицательного значения) в % на
                    чек от 0 до 99,99 % (2 байта со знаком) -9999...9999
                Налог 1 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Налог 2 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Налог 3 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Налог 4 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Текст (40 байт)
            Ответ: 85H. Длина сообщения: 8 байт.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 1...30
                Сдача (5 байт) 0000000000...9999999999
        """
        return self.wrap("x85",cash,summs,discount,taxes,text)

    def cancelCheck(self):
        """ Отмена чека
            Алиас для x88() 
                Пароль ЦТО или пароль системного администратора, если
                    пароль ЦТО не был установлен (4 байта)
                Код устройства (1 байт)
                    01 – накопитель ФП 1
                    02 – накопитель ФП 2
                    03 – часы
                    04 – энергонезависимая память
                    05 – процессор ФП
                    06 – память программ ККТ
                    07 – оперативная память ККТ
            Ответ: 01H. Длина сообщения: 4 байта.
                Код ошибки (1 байт)
                Количество блоков данных (2 байта)
        """
        return self.wrap("x88")

    def sale(self, sale_type, price, text='', count=1, department=0, taxes=[0,0,0,0]):
        """ Продажа
            Команда: 80H. Длина сообщения: 60 байт.
                Пароль оператора (4 байта)
                Количество (5 байт) 0000000000...9999999999
                Цена (5 байт) 0000000000...9999999999
                Номер отдела (1 байт) 0...16
                Налог 1 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Налог 2 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Налог 3 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Налог 4 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                Текст (40 байт)
            Ответ: 80H. Длина сообщения: 3 байта.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 1...30
        """
        return self.wrap("_x8count",self.sale_types[sale_type],count,price,text,department,taxes)

    def printString(self, text='', control_tape=False):
        """ Печать строки без ограничения на 36 символов
            В документации указано 40, но 4 символа выходят за область
            печати на ФРК. 
        """
        return self.wrap("x17_loop",text,control_tape)

    def printBarcode(self,barcode):
        """ Печать штрих-кода
            Команда: C2H. Длина сообщения: 10 байт.
                Пароль оператора (4 байта)
                Штрих-код (5 байт) 000000000000...999999999999
            Ответ: С2H. Длина сообщения: 3 байта.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 1...30
        """
        return self.wrap("xC2",barcode)

    def x10_enh(self):
        """ Короткий запрос состояния ФР
            Команда: 10H. Длина сообщения: 5 байт.
                Пароль оператора (4 байта)
            Ответ: 10H. Длина сообщения: 16 байт.
                Код ошибки (1 байт)
                Порядковый номер оператора (1 байт) 1...30
                Флаги ККТ (2 байта)
                Режим ККТ (1 байт)
                Подрежим ККТ (1 байт)
                Количество операций в чеке (1 байт) младший байт
                    двухбайтного числа (см. документацию)
                Напряжение резервной батареи (1 байт)
                Напряжение источника питания (1 байт)
                Код ошибки ФП (1 байт)
                Код ошибки ЭКЛЗ (1 байт)
                Количество операций в чеке (1 байт) старший байт
                    двухбайтного числа (см. документацию)
                Зарезервировано (3 байта)
        """
        command = 0x10
        params = self.admin_password
        data, error, command = self.ask(command,params)

        # Флаги ККТ
        kkt_flags = kkt.string2bits(data[2] + data[1]) # старший байт и младший байт
        kkt_flags = [ kkt.KKT_FLAGS[i] for i, x in enumerate(kkt_flags) if x ] 
        # Количество операций
        operations = kkt.int2.unpack(data[10]+data[5]) # старший байт и младший байт

        result = {
            'error':           error,
            'operator':        ord(data[0]),
            'kkt_flags':       kkt_flags,
            'kkt_mode':        ord(data[3]),
            'kkt_submode':     ord(data[4]),
            'voltage_battery': ord(data[6]),
            'voltage_power':   ord(data[7]),
            'fp_error':        ord(data[8]),
            'eklz_error':      ord(data[9]),
            'operations':      operations,
            'reserve':         data[11:],
        }
        return result

class KilyKktError(kkt.KktError):
    pass

import datetime
import time
from urllib import parse
import requests
import pandas as pd

class Moex:
    def query(self, method : str, **kwargs):
        """
        Отправляю запрос к ISS MOEX
        :param method:
        :param kwargs:
        :return:
        """
        try:
            url = "https://iss.moex.com/iss/%s.json" % method
            if kwargs:
                if '_from' in kwargs: kwargs['from'] = kwargs.pop('_from') # костыль - from нельзя указывать как аргумент фн, но в iss оно часто исп
                url += "?" + parse.urlencode(kwargs)

            # не обязательно
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',}

            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            j = r.json()
            return j

        except Exception as e:
            print("query error %s" % str(e))
            return None

    def flatten(self, j:dict, blockname:str):
        """
        Собираю двумерный массив (словарь)
        :param j:
        :param blockname:
        :return:
        """
        return [{str.lower(k) : r[i] for i, k in enumerate(j[blockname]['columns'])} for r in j[blockname]['data']]

    def rows_to_dict(self, j:dict, blockname:str, field_key='name', field_value='value'):
        """
        Для преобразования запросов типа /securities/:secid.json (спецификация бумаги)
        в словарь значений
        :param j:
        :param blockname:
        :param field_key:
        :param field_value:
        :return:
        """
        return {str.lower(r[field_key]) : r[field_value] for r in self.flatten(j, blockname)}

    def get_bonds(self, page=1, limit=10):
        """
        Получаю облигации торгуемые на Мосбирже (stock_bonds)
        без данных по облигации, только исин, эмитент и т.п.
        :param page:
        :param limit:
        :return:
        """
        j = self.query("securities", group_by="group", group_by_filter="stock_bonds", limit=limit, start=(page-1)*limit)
        f = self.flatten(j, 'securities')
        return f

    def get_specs(self, secid : str):
        return self.rows_to_dict(self.query(f"securities/{secid}"), 'description')

    def get_yield(self, secid: str):
        path = f"history/engines/stock/markets/bonds/sessions/3/securities/{secid}"
        _from = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        _r = self.flatten(self.query(path, _from=_from), 'history')

        # если сделок не было, то что-то нужно записать в базу чтобы не запрашивать облигу сегодня ещё
        # todo: проверить - гипотетически пустые ответы могут быть сбоем
        if len(_r) < 1: return {'price' : 0, 'yieldsec' : 0, 'tradedate' : datetime.datetime.now().strftime("%Y-%m-%d"), 'volume' : 0}

        return {
            'price' : _r[-1]['close'],
            'yieldsec' : _r[-1]['yieldclose'],
            'tradedate' : _r[-1]['tradedate'],
            'volume' : _r[-1]['volume'],
        }

    def get_last_yield(self, secid: str):
        """
        !!! Сейчас не использую, вместо него см.
        https://iss.moex.com/iss/reference/793
        Очень кривой способ
        - расчет вчерашним днем
        - нет объемов (стакан платный)
        - не ко всем бумагам
        - глючит

        price = Column(Float)
        tradedate = Column(DateTime)
        effectiveyield = Column(Float)

        :param secid:
        :return:
        """
        path = f"history/engines/stock/markets/bonds/yields/{secid}"
        _from = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        _r = self.flatten( self.query(path, _from=_from), 'history_yields')

        # не по всем облигам (особ не публичным) вообще есть такая инфа
        r = {} if _r is None or len(_r) < 1 else _r[-1]
        # не для всех облиг есть торговля, но нужно в базе как то отмечать что проверка была, поэтому костыль ниже
        k = 'tradedate'
        if k not in r or r[k] is None: r[k] = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        return r

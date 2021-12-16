from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Bond(Base):
    """
    https://www.moex.com/ru/listing/securities.aspx
    https://www.moex.com/ru/issue.aspx?code=secid
    https://www.moex.com/ru/issue.aspx?code=RU000A1047S3

    К сож. в беспл ISS MOEX не доступны orderbook ни в каком видео
    """
    __tablename__ = "bonds"
    id = Column(Integer, primary_key=True)
    secid = Column(String)
    shortname = Column(String)

    price = Column(Float) # цена в проц от номинала
    tradedate = Column(DateTime) # дата посл торгов, если при последней проверке торгов не было - заношу дату проверки
    yieldsec = Column(Float) # расчитанная мосбиржей доходность в соотв. запросе (может отличаться нюансами)
    volume = Column(Integer) # объем торгов на посл сессиий в выбраном режиме торгов (board)
    matdate = Column(DateTime) # Дата погашения
    couponfrequency = Column(Integer) # частота выплаты купона
    couponpercent = Column(Float) # купон %
    listlevel = Column(Integer) # Уровень листинга - 1 круто, 3 - нет

    updated = Column(DateTime)

    is_traded = Column(Boolean)
    emitent_id = Column(Integer)
    type = Column(String) # тип облиги (корп, офз, муниц)
    primary_boardid = Column(String) # осн. режим торгов (board)

    issuedate = Column(DateTime) # Дата начала торгов
    initialfacevalue = Column(Integer) # Первоначальная номинальная стоимость
    faceunit = Column(String) # валюта
    issuesize = Column(Integer) # объем выпуска
    facevalue = Column(Float) # Номинальная стоимость
    coupondate = Column(DateTime) # дата след купона (при условии обновленной базы)
    couponvalue = Column(Float) # купон нв деньгах
    isqualifiedinvestors = Column(Boolean) # только для квалов
    earlyrepayment = Column(Boolean) # Возможен досрочный выкуп



    def cast(self, val, _type, _key):
        """
        Приведение типов
        ISS не всегда отдает number в нужном видео, иногда number в ответе - это str, соотв нужно привести
        Даты тоже нужно привести к datetime
        :param val:
        :param _type:
        :param _key:
        :return:
        """
        try:
            if not val: return val

            if isinstance(_type, Integer) : val = int(val)
            elif isinstance(_type, String) : val = str(val)
            elif isinstance(_type, Float) : val = float(val)
            elif isinstance(_type, Boolean) : val = int(val) # для sqllite так
            elif isinstance(_type, DateTime) : val = datetime.strptime(val, "%Y-%m-%d")
        except Exception as e:
            # для дебага
            print([val, _type, _key, self.secid])
            exit(0)

        return val

    def from_json(self, j):
        """
        Данные из json формата в модель по аттрибутам
        минус способа - аттрибуты должно одинаково именоваться json => model => table
        это не всегда удобно
        :param j:
        :return:
        """
        for col in self.__table__.columns:
            if col.key in j:
                val = self.cast(j[col.key], col.type, col.key)
                setattr(self, col.key, val)


    def get_date_str(self, field = 'issuedate', _format = '%Y-%m-%d'):
        """
        Формат поля даты из timestamp в строку формата _format
        :param field:
        :param _format:
        :return:
        """
        val = getattr(self, field)
        if not val : return "n/a"
        return val.strftime('%Y-%m-%d')

    def get_url(self):
        """
        Инфа по выпуску
        https://www.tinkoff.ru/invest/bonds/{secid}/

        :return:
        """
        return f"https://www.moex.com/ru/issue.aspx?code={self.secid}"

    def __str__(self):
        issuedate = self.get_date_str()
        tradedate = self.get_date_str('tradedate')
        return f"{self.secid} / {self.shortname}, {issuedate} = {self.is_traded} / {tradedate} = {self.yieldsec}"

from datetime import datetime, timedelta
from importlib import resources

from sqlalchemy import create_engine, func, desc, and_, or_
from sqlalchemy.orm import sessionmaker

from inc.Models import Bond
import pandas as pd

class Db:
    def __init__(self):
        with resources.path("_db", "db.db") as path:
            engine = create_engine(f"sqlite:///{path}")
            _session = sessionmaker()
            _session.configure(bind=engine)
            self.session = _session()

    def get_df(self):
        return pd.read_sql(self.session.query(Bond).statement, self.session.bind)


    def add_bond(self, j):
        """
        Добавляю новую облигу
        или обновляю ту что уже в базе
        :param j:
        :return:
        """
        o = self.session.query(Bond).filter_by(secid=j['secid']).first()
        if not o: o = Bond()

        o.from_json(j)
        self.session.add(o)

    def update_bond_from_json(self, bond : Bond, j:dict):
        """
        Обновление облиги
        запись спеков и доходностей
        :param bond:
        :param j:
        :return:
        """
        bond.from_json(j)
        bond.updated = datetime.now()
        self.session.add(bond)

    def get_random_bond(self) -> Bond:
        return self.session.query(Bond).filter_by(is_traded=True).order_by(func.random()).first()

    def get_next_bond(self, seconds = 18000 ) -> Bond:
        before = (datetime.now() - timedelta(seconds=seconds))
        return self.session.query(Bond).filter(and_( or_(Bond.updated == None, Bond.updated < before), Bond.is_traded == True)).order_by(desc(Bond.updated)).first()
from datetime import datetime, timedelta

import pandas as pd

from inc.Db import Db

class Analytics:
    def __init__(self, db : Db):
        self.df = db.get_df()
        self.df['matdays'] = self.df['matdate'] - datetime.now()

    def get_main_stats(self):
        date_2022 = datetime.strptime("2022-01-01", "%Y-%m-%d")
        date_2021 = datetime.strptime("2021-01-01", "%Y-%m-%d")
        date_2020 = datetime.strptime("2020-01-01", "%Y-%m-%d")
        date_2019 = datetime.strptime("2019-01-01", "%Y-%m-%d")
        delta365 = timedelta(days=365)
        df = self.df
        
        stats = {
            'всего облиг' : len(df.index),
            'торгуемых' : len(df[ df['is_traded'] == 1].index),
            'для квалов' : len(df[ df['isqualifiedinvestors'] == True].index),

            'выпущенных в 2021' : len(df[ (df['issuedate'] >= date_2021) & (df['issuedate'] <= date_2022)].index),
            'выпущенных в 2020' : len(df[ (df['issuedate'] >= date_2020) & (df['issuedate'] <= date_2021)].index),
            'выпущенных в 2019' : len(df[ (df['issuedate'] >= date_2019) & (df['issuedate'] <= date_2020)].index),

            'с доходностью > 1%' : len(df[ df['effectiveyield'] >= 1].index),
            'с доходностью > 8%' : len(df[ df['effectiveyield'] >= 8].index),
            'с доходностью > 11%' : len(df[ df['effectiveyield'] >= 11].index),

            'листинг 1' : len(df[ (df['is_traded'] == 1) & (df['listlevel'] == 1)].index),
            'медианная доходность, листинг 1, %' : round(df[ (df['is_traded'] == 1) & (df['listlevel'] == 1)]['effectiveyield'].median(),2),
            'листинг 2' : len(df[ (df['is_traded'] == 1) & (df['listlevel'] == 2)].index),
            'медианная доходность, листинг 2, %' : round(df[ (df['is_traded'] == 1) & (df['listlevel'] == 2)]['effectiveyield'].median(),2),
            'листинг 3' : len(df[ (df['is_traded'] == 1) & (df['listlevel'] == 3)].index),
            'медианная доходность, листинг 3, %' : round(df[ (df['is_traded'] == 1) & (df['listlevel'] == 3)]['effectiveyield'].median(),2),

            'медианная цена, %' : round(df['price'].mean(),2),

            'медианная цена, с дох >= 11, %' : round(df[ df['effectiveyield'] >= 11]['price'].median(),2),
            'медианная цена, с дох >= 8 & < 11, %' : round(df[ (df['effectiveyield'] >= 8) & (df['effectiveyield'] < 11)]['price'].median(),2),
            'медианная цена, с дох >= 1 & < 8, %' : round(df[ (df['effectiveyield'] >= 1) & (df['effectiveyield'] < 8)]['price'].median(),2),

            'медианная цена, листинг 1, %' : round(df[ (df['is_traded'] == 1) & (df['listlevel'] == 1)]['price'].median(),2),
            'медианная цена, листинг 2, %' : round(df[ (df['is_traded'] == 1) & (df['listlevel'] == 2)]['price'].median(),2),
            'медианная цена, листинг 3, %' : round(df[ (df['is_traded'] == 1) & (df['listlevel'] == 3)]['price'].median(),2),

            'медианная цена, matday < 365, %' : round(df[df['matdays'] < delta365]['price'].median(),2),
            'медианная доходность, matday < 365, %' : round(df[df['matdays'] < delta365]['effectiveyield'].median(),2),

        }

        return stats

    def report_lowest_price(self, min_normal=90):
        return self.df[self.df['price'] < min_normal].sort_values(by=['effectiveyield'], ascending=False)

    def report_365_cheap_ll21(self):
        """
        Облиги с ценой ниже медианы, в лл 1-2 и с погашением в сл 365 дней
        :return:
        """
        delta365 = timedelta(days=365)
        df = self.df[ (self.df['is_traded'] == 1) & (self.df['listlevel'] == 2) & (self.df['matdays'] < delta365)]
        med = df['price'].median()
        return df[df['price'] < med].sort_values(by=['price'], ascending=True)

    def report_365_yieldest(self):
        """
        Облиги погашаемые в след 365 дней и в листингах 1 и 2
        доходностью выше медианной в этой группе
        :return:
        """
        delta365 = timedelta(days=365)
        df = self.df[(self.df['matdays'] < delta365) & (self.df['listlevel'] <= 2)]
        med = df['effectiveyield'].median()
        return df[df['effectiveyield'] > med].sort_values(by=['effectiveyield'], ascending=False)


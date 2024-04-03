# -*- coding: utf-8 -*-
# @Time    : 2023/12/16 15:49 15:49
# @Author  : Zr
# @Comment :
import akshare
import datetime
import pandas as pd


class AkShareFreq:
    Day = 'daily'
    Week = 'weekly'
    Mon = 'monthly'


def get_bars(code,
             start_date=None,
             end_date=None,
             freq='daily',
             adjust="",
             ):
    if not end_date:
        end_date = datetime.datetime.today().strftime('%Y%m%d')
    else:
        end_date = end_date.replace('-', '')
    if not start_date:
        start_date = '19000101'
    else:
        start_date = start_date.replace('-', '')

    # f freq not in ('d', 'w', 'm', 'D', 'W', 'M'):
    #    raise Exception('error freq=%s' % freq)

    df = akshare.stock_zh_a_hist(symbol=code, period=freq, start_date=start_date, end_date=end_date, adjust=adjust)
    if not df.empty:
        # count = df.shape[0]
        df.rename(columns={
            '日期': 'date',  # pd.to_datetime.dt.date
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '涨跌幅': 'change_pct',
            "换手率": 'turnover'
        }, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df.drop(['涨跌额'], axis=1, inplace=True)
        df.drop(['振幅'], axis=1, inplace=True)
        df.rename(columns={'date': 'datetime'}, inplace=True)

    return df

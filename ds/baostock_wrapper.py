# -*- coding: utf-8 -*-
# @Time    : 2023/12/16 15:51 15:51
# @Author  : Zr
# @Comment :
import datetime
import baostock as bs
import pandas as pd
import util
from log import logger

bs.login()


class BaoStockFreq:
    FiveMinute = '5'
    FifteenMinue = '15'
    ThirtyMinute = '30'
    SixtyMinute = '60'
    Day = 'd'
    Week = 'w'
    Mon = 'm'


def _convert_code(code):
    '''
    000001 => sz.000001
    :param code:
    :return:
    '''
    if not code: raise Exception('Error code: %s' % code)
    exchange = util.get_market(code)
    return exchange + '.' + code


def _format_numeric(df):
    map = {
        'open': 'float64',
        'close': 'float64',
        'high': 'float64',
        'low': 'float64',
        'volume': 'int64',
        'amount': 'float64',
        'turnover': 'float64',
        'change_pct': 'float64'
    }
    for k, v in map.items():
        if k in df.columns:
            df[k] = df[k].astype(v)
            if v == 'float64':
                df[k] = df[k].round(2)


def get_factors(code, start_date, end_date=None):
    if not end_date:
        end_date = datetime.datetime.today().strftime('%Y-%m-%d')
    rs_list = []
    bscode = _convert_code(code)
    rs_factor = bs.query_adjust_factor(code=bscode, start_date=start_date, end_date=end_date)
    while (rs_factor.error_code == '0') & rs_factor.next():
        rs_list.append(rs_factor.get_row_data())
    result_factors = pd.DataFrame(rs_list, columns=rs_factor.fields)

    return result_factors


def get_bars(code, start_date=None, end_date=None, freq='d', adjust=None):
    if adjust == 'qfq':
        _adjust = '2'
    elif adjust == 'hfq':
        _adjust = '1'
    else:
        _adjust = '3'

    if not end_date:
        end_date = datetime.datetime.today().strftime('%Y-%m-%d')

    if freq == 'd':
        fields = "date,open,close,high,low,volume,amount,pctChg,turn"
    elif freq in ('5', '15', '30', '60'):
        fields = "time,close,open,high,low,volume,amount"
    else:
        raise Exception('freq=%s, not supported yet.' % freq)

    bscode = _convert_code(code)
    rs = bs.query_history_k_data_plus(bscode,
                                      fields,
                                      start_date=start_date,
                                      end_date=end_date,
                                      frequency=freq,
                                      adjustflag=_adjust)
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)
    _columns = {
        'turn': 'turnover',
        'pctChg': 'change_pct'
    }
    df.replace("", pd.NA, inplace=True)
    if 'time' in df.columns:
        df['time'] = df['time'].str.slice(0, 14)
        df['time'] = pd.to_datetime(df['time'], format='%Y%m%d%H%M%S')
        _columns.update({'time': 'datetime'})
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        _columns.update({'date': 'datetime'})
    df.rename(columns=_columns, inplace=True)

    df = df[~df['volume'].isna()]
    _format_numeric(df)

    return df

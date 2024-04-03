# -*- coding: utf-8 -*-
# @Time    : 2023/11/25 16:06
# @Author  : Zr
# @Comment :
import datetime
import os
import pickle
import pandas as pd
import akshare as ak
from config import CODE_FILE, TRADE_DATA_DIR
from log import logger


def get_market(code):
    exchange = ''
    if code.find('6', 0, 1) == 0:
        exchange = 'sh'
    elif code.find('3', 0, 1) == 0:
        exchange = 'sz'
    elif code.find('0', 0, 1) == 0:
        exchange = 'sz'
    elif code.find('4', 0, 1) == 0:
        exchange = 'bj'
    elif code.find('8', 0, 1) == 0:
        exchange = 'bj'
    else:
        raise Exception('Error code:%s' % code)
    return exchange


def read(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None


def write(path, obj):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def get_stock_list(exclude_market=None):
    sdf = pd.read_feather(CODE_FILE)
    if type(exclude_market) is str:
        exclude_market = [exclude_market]

    if exclude_market:
        sdf = sdf[~sdf['market'].isin(exclude_market)]

    return sdf['code'].tolist()


def get_exchange_trading_dates(start_date='2005-01-01'):
    '''
    起始日期之后到今日的所有交易日
    :param start_date:
    :return:
    '''
    start_date = start_date.replace('-', '')
    df = ak.index_zh_a_hist(symbol='000001', start_date=start_date, period="daily")
    return df['日期'].tolist()


def get_working_dir(freq='d', type='bar'):
    '''
    :param freq: 默认为d，日k线；d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据
    :type bar|xdxr|index
    :return:
    '''
    working_dir = None
    if type == 'bar':
        # freq = freq.lower()
        if freq not in ['tick', 'fb', 'd', 'w', 'm', '1m', '5m', '15m', '30m', '60m']:
            raise Exception('freq <%s> error, type=bar' % freq)

        if freq == 'd':
            working_dir = os.path.join(TRADE_DATA_DIR, 'day')
        elif freq == 'fb':
            working_dir = os.path.join(TRADE_DATA_DIR, 'fb')
        elif freq == 'tick':
            working_dir = os.path.join(TRADE_DATA_DIR, 'tick')
        elif freq == 'w':
            working_dir = os.path.join(TRADE_DATA_DIR, 'week')
        elif freq == 'm':
            working_dir = os.path.join(TRADE_DATA_DIR, 'mon')
        elif freq == '1m':
            working_dir = os.path.join(TRADE_DATA_DIR, '1min')
        elif freq == '5m':
            working_dir = os.path.join(TRADE_DATA_DIR, '5min')
        elif freq == '15m':
            working_dir = os.path.join(TRADE_DATA_DIR, '15min')
        elif freq == '30m':
            working_dir = os.path.join(TRADE_DATA_DIR, '30min')
        elif freq == '60m':
            working_dir = os.path.join(TRADE_DATA_DIR, '60min')
    elif type == 'xdxr':
        working_dir = os.path.join(TRADE_DATA_DIR, 'xdxr')
    elif type == 'index':
        # freq = freq.lower()
        if freq not in ['d', 'w', 'm']:
            raise Exception('freq <%s> error, type=index' % freq)

        if freq == 'd':
            working_dir = os.path.join(TRADE_DATA_DIR, 'index', 'day')
        elif freq == 'w':
            working_dir = os.path.join(TRADE_DATA_DIR, 'index', 'week')
        elif freq == 'm':
            working_dir = os.path.join(TRADE_DATA_DIR, 'index', 'mon')
        '''
        elif freq == '1m':
            working_dir = os.path.join(TRADE_DATA_DIR,'index', '1min')
        elif freq == '5m':
            working_dir = os.path.join(TRADE_DATA_DIR,'index', '5min')
        elif freq == '15m':
            working_dir = os.path.join(TRADE_DATA_DIR, 'index','15min')
        elif freq == '30m':
            working_dir = os.path.join(TRADE_DATA_DIR, 'index','30min')
        elif freq == '60m':
            working_dir = os.path.join(TRADE_DATA_DIR, 'index','60min')
        '''
    else:
        raise Exception('type <%s> error, freq=%s' % (type, freq))

    if not os.path.exists(working_dir): os.makedirs(working_dir)

    return working_dir


def get_bar(code, start_date=None, end_date=None, freq='d', index=False):
    wd = get_working_dir(freq=freq, type='index' if index else 'bar')
    f = os.path.join(wd, '%s.ftr' % code)
    if not os.path.exists(f):
        raise Exception('local data file not found, path: %s' % f)

    df = pd.read_feather(f)
    if not end_date:
        end_date = datetime.datetime.today()
    if not start_date:
        start_date = datetime.datetime.strptime('1900-01-01', '%Y-%m-%d')
    if freq == 'd':
        return df[(df['date'] >= start_date) & (df['date'] < end_date)]
    elif freq in ('5m', '15m', '30m', '60m'):
        return df[(df['time'] >= start_date) & (df['time'] < end_date)]


def trading_dates_to_update(code_file):
    day_file = os.path.join(TRADE_DATA_DIR, 'day', os.path.basename(code_file))
    df_dates = pd.read_feather(day_file)['datetime']

    dt_start = datetime.datetime.strptime('1900-01-01', '%Y-%m-%d')
    '''
    if not end:
        dt_end = datetime.datetime.today()
    else:
        dt_end = datetime.datetime.strptime(end, '%Y-%m-%d')
    '''

    if os.path.exists(code_file):
        df = pd.read_feather(code_file)
        last_date = df['datetime'].max()
        logger.debug('local code file most recently updated date: %s', last_date)
    else:
        last_date = dt_start

    # dates = df_dates[(df_dates > last_date) & (df_dates < dt_end)]
    dates = df_dates[(df_dates > last_date)]
    return [d.strftime('%Y-%m-%d') for d in dates.tolist()]


# -*- coding: utf-8 -*-
# @Time    : 2023/11/29 22:30 22:30
# @Author  : Zr
# @Comment :
import datetime
import os.path

from zqdata import config
import pandas as pd
import akshare as ak


class CodeType:
    '''
    CODE: 000001
    CODE_MARKET: 000001.sh
    CODE_ISO: 000001.XSHG
    MARKET_CODE: sh.000001
    '''
    CODE = 0
    CODE_MARKET = 1
    CODE_MARKET_CAP = 11
    CODE_ISO = 2
    MARKET_CODE = 3
    MARKET_CODE_CAP = 31


def get_trade_days(start_date=None, end_date=None):
    '''
     起始日期之后到今日的所有交易日
     :param start_date:
     :return:
     '''

    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')  # start_date.replace('-', '')
    # end_date = end_date.replace('-', '')
    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    df = ak.index_zh_a_hist(symbol='000001', start_date=start_date, end_date=end_date, period="daily")

    return df['日期'].tolist()


def get_all_stock(market=None):
    df = pd.read_feather(config.CODE_FILE)
    if market:
        market = market.lower()
        if market not in ('sz', 'sh', 'bj'):
            raise Exception('market must be one of (sz, sh, bj)')
        return df[df['market'] == market]
    return df


def _market(code):
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


def code_convert(code, type=CodeType.CODE_MARKET):
    if type == CodeType.CODE:
        return code.split('.')[0]
    elif type == CodeType.CODE_MARKET:
        return '%s.%s' % (code, _market(code))
    elif type == CodeType.CODE_MARKET_CAP:
        return '%s.%s' % (code, _market(code).upper())
    elif type == CodeType.CODE_ISO:
        return '%s.%s' % (code, 'XSHG' if _market(code) == 'sh' else 'XSHE')
    elif type == CodeType.MARKET_CODE:
        return '%s.%s' % (_market(code), code)
    elif type == CodeType.MARKET_CODE_CAP:
        return '%s.%s' % (_market(code).upper(), code)
    else:
        raise Exception('Error code:%s' % code)


if __name__ == '__main__':
    df_codes = get_all_stock(market='sz')
    cc = [code_convert(code, type=CodeType.CODE_ISO) for code in df_codes['code'].tolist()]
    df_codes = get_all_stock(market='sh')
    cc = cc + [code_convert(code, type=CodeType.CODE_ISO) for code in df_codes['code'].tolist()]
    import json

    for code in cc:
        code1 = code.split('.')[0]
        fpath = os.path.join(config.TRADE_DATA_DIR, 'day', '%s.ftr' % code1)
        print('current code: %s' % code)
        if os.path.exists(fpath):
            df = pd.read_feather(fpath)
            df = df[df['date'] >= datetime.datetime.strptime('2010-01-01', '%Y-%m-%d')]
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            with open('D:\\projects\\fin_stock_data\\pptrs\\jq\\%s.json' % code, 'w+') as f:
                json.dump(df['date'].tolist(), f)
        else:
            print('remove code: %s' % code)
            cc.remove(code)

    with open('D:\\projects\\fin_stock_data\\pptrs\\jq\\code.json', 'w+') as f:
        json.dump(cc, f)

    exit()

    c = code_convert('000001', CodeType.CODE)
    print(c)

    c = code_convert('000001', CodeType.CODE_MARKET)
    print(c)

    c = code_convert('000001', CodeType.CODE_MARKET_CAP)
    print(c)

    c = code_convert('000001', CodeType.CODE_ISO)
    print(c)

    c = code_convert('000001', CodeType.MARKET_CODE)
    print(c)

    c = code_convert('000001', CodeType.MARKET_CODE_CAP)
    print(c)

    df = get_all_stock('bj')
    print(df.shape[0])
    print(df.tail(1))

    dt = get_trade_days('2023-06-01', '2023-06-30')
    print(dt)

    dt = get_trade_days(start_date='2023-11-01')
    print(dt)

    dt = get_trade_days(end_date='1990-12-25')
    print(dt)

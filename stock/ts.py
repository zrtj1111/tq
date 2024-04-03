# -*- coding: utf-8 -*-
# @Time    : 2023/11/29 14:41 14:41
# @Author  : Zr
# @Comment :
import datetime
import os.path

import pandas as pd
from ds import akshare_wrapper as aw
import config
import util
from mootdx.utils.adjust import fq_factor


def get_bars(code, freq='d', start_date=None, end_date=None, adjust=None, source='tdx'):
    f = os.path.join(util.get_working_dir(freq), '%s.ftr' % code)
    if not os.path.exists(f):
        raise Exception('%s local data not exists~' % code)
    df = pd.read_feather(f)

    if adjust:
        if adjust not in ['qfq', 'hfq']:
            raise Exception('Error adjust, must be <qfq|hfq>')

        xdxr_file = os.path.join(util.get_working_dir(type='xdxr'), '%s.ftr' % code)

        df_xdxr = pd.read_feather(xdxr_file)
        df = pd.merge(df, df_xdxr, on='datetime', how='left')
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col] * df['factor']
            df[col] = df[col].round(2)

    if start_date:
        df = df[df['datetime'] >= datetime.datetime.strptime(start_date, '%Y-%m-%d')]
    if end_date:
        df = df[df['datetime'] <= datetime.datetime.strptime(end_date, '%Y-%m-%d')]

    return df


if __name__ == '__main__':
    import ds.baostock_wrapper as bw
    import ds.akshare_wrapper as aw
    import ds.mootdx_wrapper as mw

    df = get_bars('600081', start_date='2022-08-16', adjust='qfq').head(2)
    print(df, df.dtypes)

    df = bw.get_bars('600081', start_date='2022-08-16', end_date='2022-08-17', freq=bw.BaoStockFreq.Day,
                     adjust='qfq')
    print(df, df.dtypes)

    df = aw.get_bars('600081', start_date='2022-08-16', end_date='2022-08-17', freq=aw.AkShareFreq.Day,
                     adjust='qfq')
    print(df, df.dtypes)

# -*- coding: utf-8 -*-
# @Time    : 2023/12/3 11:15 11:15
# @Author  : Zr
# @Comment :
import datetime

from mootdx.quotes import Quotes
import pandas as pd
import util
import numpy as np


class TdxFreq:
    OneMinute = 7
    FiveMinute = 0
    FifteenMinue = 1
    ThirtyMinute = 2
    SixtyMinute = 3
    Day = 4
    Week = 5
    Mon = 6


offset = 800


def get_bars(code, start_date=None, freq=TdxFreq.Day, adjust='qfq'):
    client = Quotes.factory(market='std', adjust=adjust)

    start = 0
    df = None
    while True:
        df_chunk = client.bars(symbol=code, frequency=freq, offset=offset, start=start, adjust=adjust)
        if df_chunk.empty:
            break

        df_chunk.drop(['datetime', 'year', 'month', 'day', 'minute', 'hour', 'vol'], inplace=True, axis=1)
        df_chunk.reset_index(inplace=True)
        df_chunk['volume'] = df_chunk['volume'].astype('int64')

        if df is None:
            df = df_chunk
        else:
            df = pd.concat([df_chunk, df], ignore_index=True)

        if start_date:
            dt_start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            df_early = df[df['datetime'] <= dt_start]
            if not df_early.empty:
                df = df[df['datetime'] >= dt_start]
                break

        start = start + offset

    if df is None:
        df = pd.DataFrame(columns=['datetime', 'open', 'close', 'high', 'low', 'volume', 'amount'])

    return df[['datetime', 'open', 'close', 'high', 'low', 'volume', 'amount']]

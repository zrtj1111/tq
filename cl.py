# -*- coding: utf-8 -*-
import sqlite3
import webbrowser
import pandas as pd
from ds import akshare_wrapper as aw
import matplotlib.pyplot as plt
from pyecharts import options as opts
from pyecharts.charts import Kline
from pyecharts.options import InitOpts
import numpy as np

db_file = 'trends.db'


class CFenxi:
    '''
    分形必包含3个bar
    '''
    UP = 1
    DOWN = 0

    def __init__(self, c1, c2, c3):
        self.position = c2.position
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3

    @property
    def direction(self):
        if self.c2.high > self.c1.high and self.c2.high > self.c3.high:
            return CFenxi.UP
        elif self.c2.low < self.c1.low and self.c2.low < self.c3.low:
            return CFenxi.DOWN
        else:
            raise Exception('Error Fenxi')

    @property
    def high(self):
        return max(self.c1.high, self.c2.high, self.c3.high)

    @property
    def low(self):
        return min(self.c1.low, self.c2.low, self.c3.low)

    @property
    def is_up(self):
        return True if self.direction == CFenxi.UP else False

    @property
    def is_down(self):
        return True if self.direction == CFenxi.DOWN else False

    def __repr__(self):
        return "< position=%s, direction=%s, high=%s, low=%s >" % (
            self.c2.position, 'UP' if self.direction == CFenxi.UP else 'DOWN', self.c2.high, self.c2.low)


def _IS_FX(c1, c2, c3):
    if c2.high > c1.high and c2.high > c3.high:
        return CFenxi(c1=c1, c2=c2, c3=c3)
    elif c2.low < c1.low and c2.low < c3.low:
        return CFenxi(c1=c1, c2=c2, c3=c3)

    return None


class CBar:
    def __init__(self, position=None, left=None, right=None, high=None, low=None, dt=None):
        self.position = position
        self.high = high
        self.low = low
        self.left = left
        self.right = right
        self.dt = dt  # datetime

    def __repr__(self):
        return "< dt=%s, postion=%s, left=%s, right=%s, high=%s, low=%s >" % (
            self.dt, self.position, self.left, self.right, self.high, self.low)


def _take_bar(df, i=0):
    '''
    合并缠论的包含关系
    :param df: OHLC dataframe
    :param i:
    :return:
    '''
    if i >= len(df) or i < 0:
        raise Exception('i is out of bound.')

    cbar = CBar()
    n = df.take([i])

    cbar.position = i
    cbar.left = i
    cbar.right = i
    cbar.high = n['high'].values[0]
    cbar.low = n['low'].values[0]

    next = i + 1
    while next < len(df):
        n = df.take([next])

        # 右包含关系, 一定先做右包含
        if n['high'].values[0] >= cbar.high and n['low'].values[0] <= cbar.low:
            cbar.position = next
            cbar.right = next
            cbar.high = n['high'].values[0]
            cbar.low = n['low'].values[0]
            next += 1
            continue

        # 左包含关系
        if n['high'].values[0] <= cbar.high and n['low'].values[0] >= cbar.low:
            cbar.right = next
            next += 1
            continue

        break

    cbar.dt = df.loc[cbar.position, 'datetime']

    return cbar


def _fx_distance(fx1, fx2):
    return fx2.c1.left - fx1.c3.right


def find_bi(df, start=0, fx_min_distance=1):
    '''

    :param df:
    :param start:
    :param fx_min_distance: 两个分形直接要相隔多少根bar，按缠论定义，两个分形之间至少要有1个bar
    :return:
    '''
    fx_list = []
    c1 = None
    c2 = None
    while start < len(df):
        c3 = _take_bar(df, start)
        start = c3.right + 1
        if not c1:
            c1 = c3
            continue
        if not c2:
            c2 = c3
            continue

        fx = _IS_FX(c1, c2, c3)
        if fx:
            if not fx_list:
                fx_list.append(fx)
            else:
                # 与前一个分形同方向，做替换
                if fx_list[-1].direction == fx.direction:
                    if fx_list[-1].is_up:
                        fx = max(fx_list[-1], fx, key=lambda fx: fx.high)
                    else:
                        fx = min(fx_list[-1], fx, key=lambda fx: fx.low)
                    fx_list.pop()
                    fx_list.append(fx)
                else:
                    _distance = _fx_distance(fx_list[-1], fx)
                    if _distance < fx_min_distance:
                        if fx_list[-1].is_up:
                            if fx_list[-1].high <= fx.high:
                                fx_list.pop()
                        else:
                            if fx_list[-1].low >= fx.low:
                                fx_list.pop()
                    else:
                        if fx_list[-1].is_up:
                            if fx_list[-1].low > fx.low:
                                fx_list.append(fx)
                        else:
                            if fx_list[-1].high < fx.high:
                                fx_list.append(fx)

        c1 = c2
        c2 = c3

    return fx_list


def trend_classify(df):
    fj = list()

    pre_position = 0
    for fx in find_bi(df):

        start_dt = df.iloc[pre_position]['datetime']  # .replace('-', '')
        end_dt = df.iloc[fx.position]['datetime']  # .replace('-', '')

        df_sub = df.iloc[pre_position:fx.position]
        if df_sub.shape[0] < 5:
            continue
        # l = linregress(df_sub)
        # x = np.arange(pre_position, pre_position + df_sub.shape[0])
        # y = (np.arange(0, df_sub.shape[0])) * l.slope + l.intercept
        # deg = slope2degree(x, y)

        # log_rtn = np.log(df.iloc[fx.position]['close']) - np.log(df.iloc[pre_position]['close'])
        distance = (fx.position - pre_position)
        # speed = rtn / (fx.position - pre_position)
        # var = np.var(np.log(df_sub['high']) - np.log(df_sub['low']))

        # fj.append([start_dt, end_dt, rtn, speed, distance, var, l.intercept, l.slope, deg, l.stderr, l.rvalue, l.pvalue])
        fj.append([start_dt, end_dt, distance])
        pre_position = fx.position

    return pd.DataFrame(columns=['start_dt', 'end_dt', 'log_rtn', 'distance'], data=fj)


def plot_trends(code, start_date='2010-01-01', freq='d'):
    df = aw.get_bars(code=code, start_date=start_date, adjust='qfq', freq=freq)

    with sqlite3.connect(database=db_file) as con:
        df_trends = pd.read_sql('select * from stock_cl_trends where code=?', con=con, params=[code])
        df_trends.sort_values(by='start_dt', ascending=True, inplace=True)
        df_trends = df_trends[df_trends['start_dt'] >= start_date]

        for idx, r in df_trends.iterrows():
            i_start = df[df['date'] == r['start_dt']].index.tolist()[0]
            i_end = df[df['date'] == r['end_dt']].index.tolist()[0]

            _h = df.iloc[i_start]['high']
            _l = df.iloc[i_start]['low']

            x = np.arange(i_start, i_end)
            plt.plot(x, df.iloc[i_start: i_end]['close'])
            y = (np.arange(0, r['distance'])) * r['slope'] + ((_h + _l) / 2) + r['intercept']

            plt.plot(x, y)

    plt.show()


def plot(df, code, show_bi=True):
    ##plot cbar area
    mark_areas = []
    mark_points = []
    mark_lines = []
    i = 0
    while i < len(df):
        cbar = _take_bar(df, i)
        if cbar.right - cbar.left > 0:
            mark_areas.append(opts.MarkAreaItem(x=[cbar.left, cbar.right], y=[cbar.low, cbar.high]))
        i = cbar.right + 1

    if show_bi:
        fxst = find_bi(df)
        line_bi_start = None
        line_bi_end = None
        start_bar = (df.iloc[0]['high'], df.iloc[0]['low'])
        for fx in fxst:
            if not line_bi_start:
                line_bi_start = (0, start_bar[1] if fx.is_up else start_bar[0])

            if fx.is_up:
                item = opts.MarkPointItem(coord=[fx.position, fx.high], symbol='circle', symbol_size=10,
                                          itemstyle_opts=opts.ItemStyleOpts(color='#fc3aa2'))
                line_bi_end = (fx.position, fx.high)
            else:
                item = opts.MarkPointItem(coord=[fx.position, fx.low], symbol='circle', symbol_size=10,
                                          itemstyle_opts=opts.ItemStyleOpts(color="#00FF00"))
                line_bi_end = (fx.position, fx.low)

            mark_points.append(item)

            line = [opts.MarkLineItem(coord=[line_bi_start[0], line_bi_start[1]]),
                    opts.MarkLineItem(coord=[line_bi_end[0], line_bi_end[1]])]

            mark_lines.append(line)
            line_bi_start = line_bi_end

    y_data = df[['open', 'close', 'low', 'high']].values.tolist()
    # x_data = df.index.tolist()
    x_data = df['datetime'].tolist()

    kline = (
        Kline(init_opts=InitOpts(width="100%"))
        .add_xaxis(x_data)
        .add_yaxis(
            series_name="%s" % code,
            y_axis=y_data,
            markpoint_opts=opts.MarkPointOpts(
                data=mark_points
            ),
            markline_opts=opts.MarkLineOpts(
                is_silent=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.5, color='#0099CC'),
                symbol="none",
                data=mark_lines,
            ),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),

            ),
            datazoom_opts=[opts.DataZoomOpts()],
            title_opts=opts.TitleOpts(title=""),
        )
        .set_series_opts(
            markarea_opts=opts.MarkAreaOpts(
                is_silent=True,
                data=mark_areas
            )
        )
    )
    kline.render('k.html')
    webbrowser.open("k.html")


'''
def update(freq='D', retries=10):
    earliest = '1970-01-01'
    while retries > 0:
        try:
            with sqlite3.connect(database=db_file) as con:
                cur = con.cursor()
                codes = cur.execute("select * from stock_cl_trends_codes").fetchall()
                if not codes:
                    df_stocks = ak.stock_info_a_code_name()
                    codes = df_stocks['code'].tolist()
                    cur.executemany("insert into stock_cl_trends_codes values (?)", [[c] for c in codes])
                    con.commit()
                else:
                    codes = [c[0] for c in codes]

                for code in codes:

                    df_loc = pd.read_sql('select * from stock_cl_trends where code=?', con=con, params=[code])
                    if df_loc.shape[0] > 0:
                        df_loc_last = df_loc.sort_values(by='start_dt').tail(1)
                        begin = df_loc_last.iloc[0]['start_dt'].replace('-', '')
                    else:
                        begin = earliest

                    logger.debug('getting data %s, start date %s...', code, begin)
                    df = get_stock_hist(code=code, freq=freq, start_date=begin, adjust='hfq')

                    logger.debug('trend classifying...')
                    df_trends = trend_classify(df)
                    df_trends['code'] = code

                    cur.execute('delete from stock_cl_trends where code=? and start_dt=?', [code, begin])
                    df_trends.to_sql('stock_cl_trends', con=con, if_exists='append', index=False)

                    cur.execute('delete from stock_cl_trends_codes where code=?', [code])
                    logger.debug('mark done, %s...', code)
                    con.commit()
                    logger.debug('saved to database...')
            break
        except:
            logger.debug(traceback.format_exc())
            retries = retries - 1
            logger.debug('wait 10s to retry...')
            time.sleep(10)
'''

if __name__ == '__main__':
    # update()
    df = aw.get_bars('688167', start_date='2023-01-01', end_date='2023-11-31', adjust='qfq')
    # cbars = trend_classify(df)
    plot(df)
    # print(cbars)

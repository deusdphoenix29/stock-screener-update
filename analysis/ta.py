from talib import abstract
from db import db
import numpy as np
from analysis.pattern import *

today = -1


def screener(end_date):
    bounce_watch_list = []
    bounce_enter_list = []
    ip_watch_list = []
    for symbol in db.get_stock_symbol():
        open, high, low, close, date = db.get_price(symbol, end_date)
        result = bounce_strategy(symbol, open, high, low, close)
        if result and result[1] == 'watch':
            bounce_watch_list.append(symbol)
        elif result and result[1] == 'enter':
            bounce_enter_list.append(symbol)

        result = impulse_pullback(symbol, open, high, low, close)
        if result and result[1] == 'watch':
            ip_watch_list.append(symbol)
    return bounce_watch_list, bounce_enter_list, ip_watch_list


def bounce_strategy(symbol, open, high, low, close):
    result = None
    doji_list = abstract.CDLDOJI(np.array(open), np.array(high), np.array(low), np.array(close))
    ema_18 = np.round(abstract.EMA(np.array(close), timeperiod=18), 4)[today]
    ema_50 = np.round(abstract.EMA(np.array(close), timeperiod=50), 4)[today]
    macd, macdsignal, macdhist = abstract.MACD(np.array(close), fastperiod=50, slowperiod=100, signalperiod=9)
    slowk, slowd = abstract.STOCH(np.array(high), np.array(low), np.array(close), fastk_period=5, slowk_period=3,
                                  slowk_matype=0, slowd_period=3, slowd_matype=0)
    prev_reversal = {
        'open': open[today - 2],
        'high': high[today - 2],
        'low': low[today - 2],
        'close': close[today - 2],
    }
    reversal_candle = {
        'open': open[today - 1],
        'high': high[today - 1],
        'low': low[today - 1],
        'close': close[today - 1],
    }
    confirmation_candle = {
        'open': open[today],
        'high': high[today],
        'low': low[today],
        'close': close[today],
    }

    candle_pattern = False
    indicator = False

    if single_candle_reversal(reversal_candle, ema_18):
        candle_pattern = True
    if single_candle_reversal(reversal_candle, ema_50):
        candle_pattern = True
    if doji_candle_reversal(doji_list[today], reversal_candle, ema_18):
        candle_pattern = True
    if doji_candle_reversal(doji_list[today], reversal_candle, ema_50):
        candle_pattern = True
    else:
        if basic_two_candle_reversal(prev_reversal['low'], reversal_candle, ema_18):
            candle_pattern = True
        if basic_two_candle_reversal(prev_reversal['low'], reversal_candle, ema_50):
            candle_pattern = True
        else:
            if inside_bar_two_candle_reversal(prev_reversal, reversal_candle, ema_18):
                candle_pattern = True
            if inside_bar_two_candle_reversal(prev_reversal, reversal_candle, ema_50):
                candle_pattern = True
            if two_candle_reversal_trade_through(prev_reversal, reversal_candle, ema_18):
                candle_pattern = True
            if two_candle_reversal_trade_through(prev_reversal, reversal_candle, ema_50):
                candle_pattern = True

    if candle_pattern is True:
        if slowk[today] < 30:
            if macd[today] > macdsignal[today]:  # if macd is bullish
                indicator = True
            else:  # macd is bearish and not crossed bullish less than 5 days
                macd_period = macd[today - 4:]
                macd_signal_period = macdsignal[today - 4:]
                if not np.isnan(macd_period).any() \
                        and not np.isnan(macd_signal_period).any() \
                        and np.all([i < j for i, j in zip(macd_period, macd_signal_period)]):
                    indicator = True
    if indicator:
        result = (symbol, 'watch')
        if is_confirmation_candle(reversal_candle, confirmation_candle):
            # sl = np.round(confirmation_candle['low'] - 0.05, 2)
            # entry = np.round(confirmation_candle['high'] + 0.05, 2)
            # tp = np.round(entry + (entry - sl) * 2, 2)
            # signal = f'{symbol} | sl: {sl} | entry: {entry} | tp: {tp} | strategy: B'
            result = (symbol, 'enter')
    return result


def impulse_pullback(symbol, open, high, low, close):
    ema_6 = np.round(abstract.EMA(np.array(close), timeperiod=6), 4)[-3:]
    ema_18 = np.round(abstract.EMA(np.array(close), timeperiod=18), 4)[-3:]
    macd, macdsignal, macdhist = abstract.MACD(np.array(close), fastperiod=12, slowperiod=26, signalperiod=9)[-3:]
    result = None
    cross_signal = False
    if ema_6[-1] > ema_18[-1] and np.any([i < j for i, j in zip(ema_6[:-1], ema_18[:-1])]):
        cross_signal = True
    if not np.isnan(macd).any() \
            and not np.isnan(macdsignal).any() \
            and macd[-1] > macdsignal[-1] \
            and np.any([i < j for i, j in zip(macd[:-1], macdsignal[:-1])]):
        cross_signal = True
    if cross_signal and high[today] > high[today - 1]:
        return symbol, 'watch'
    return None

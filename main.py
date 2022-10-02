import requests
import time
import pandas as pd
import numpy as np
from telegram import TelegramAlert
import schedule
from log import setup_custom_logger

logger = setup_custom_logger("signal")

def upbit_5m_candle(market, minutes):
    # upbit 캔들 데이터 다운
    url = "https://api.upbit.com"
    path = "/v1/candles/minutes/" + str(minutes)
    params = {
        "market" : market,
        "count" : 200,
    }
    page_json = requests.get(url + path, params=params).json()
    df = pd.DataFrame(page_json)
    return df

def preprocessing(df):
    # upbit 서버에서 다운 받은 데이터 가공
    columns = [
        'candle_date_time_kst', 'opening_price',
        'high_price', 'low_price',
        'trade_price', 'candle_acc_trade_volume'
    ]
    df = df[columns]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume' ]
    df = df.sort_values(by='date')
    df.index = df['date']
    df.drop('date', axis=1, inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df.astype(float)
    return df

def rsi(df, source, length):
    # rsi 상대강도 지수 함수 source는 'close', 'open', 'high', 'low' 대입 가능
    # length(봉개수)는 upbit 경우 14 ~ 30 추천
    delta = df[source].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    _gain = up.ewm(com=(length - 1), min_periods=length).mean()
    _loss = down.abs().ewm(com=(length - 1), min_periods=length).mean()
    RS = _gain / _loss
    df['rsi'] = 100 - (100 / (1 + RS))
    return df

def strategy(df):
    # rsi less than 15 an greater than 85 return 1. if not return 0
    con1 = (df['rsi'] > 85)
    con2 = (df['rsi'] < 15)
    df['signal'] = np.where(con1, 1, 0)
    df['signal'] = np.where(con2, 1, 0)
    return df


def tele_signal(df, token, chat_id):
    # if signal occure, telegram message send
    signal = df.loc[:, 'signal'].values[-1]
    if signal == 1:
        TelegramAlert(token, chat_id).text('The Signal occured!!')
    elif signal == 0:
        logger.info('No Signal')


def execute(market, minutes, token, chat_id):
    # execute all functions above
    try:
        candle = upbit_5m_candle(market, minutes)
        df = preprocessing(candle)
        df = rsi(df, 'close', 14)
        df = strategy(df)
        tele_signal(df, token, chat_id)
    except:
        pass

if __name__ == "__main__":
    market  = 'KRW-BTC'
    minutes = 5 # you can change 1, 3, 5, 15 but the limit is 200
    token   = '' # put telegram token
    chat_id = '' # put telegram chat id

    # repeate all functions interval
    schedule.every(2).minutes.do(execute,
                                 market=market,
                                 minutes=minutes,
                                 token=token,
                                 chat_id=chat_id)
    while True:
        schedule.run_pending()
        time.sleep(1)

ORDER_TYPE = {
    'MARKET': 0,
    'LIMIT': 1,
    'STOP': 2,
    'CANCEL': 3,
    'MODIFY': 4,
    'STOPCANCEL': 5,

    # 선처리에서 STOP 분류를 간편하게 위해 임시로 적용되는 order_type값을 미리 선언해둠으로서 key error를 방지한다.
    # 'STOP_LIMIT': 2,
    # 'STOP_MARKET_BUY': 2,
    # 'STOP_MARKET_SELL': 2,
}

pORDER_TYPE = {v: k for (k, v) in ORDER_TYPE.items()}

SIDE = {
    'BUY': 0,
    'SELL': 1,
}

pSIDE = {v: k for (k, v) in SIDE.items()}

CANDLES = {
    'unit': ['1M', '5M', '15M', '30M', '1H', '4H', '1D', '1W'],
}

CURRENCY_ID = {
    "BASE_DSP_CURRENCY_ID": 1
}

pCURRENCY_ID = {v: k for (k, v) in CURRENCY_ID.items()}

ORDER_HISTORY_TYPE = {
    'BUY': (0,),
    'SELL': (1,),
    'ALL': (0, 1),
    'MARKET': 0,
    'LIMIT': 1
}

pORDER_HISTORY_TYPE = {v: k for (k, v) in ORDER_HISTORY_TYPE.items()}

STOP_ORDER = {
    'NO': 0,
    'YES': 1,
}

pSTOP_ORDER = {v: k for (k, v) in STOP_ORDER.items()}

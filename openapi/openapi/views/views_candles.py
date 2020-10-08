from lib.ApiView import ApiView
from lib import define
from lib.ApiView.Argument import Argument


class CandlesView(ApiView):
    DB_READONLY = True
    VERIFY_KEY = 'APIKEY'
    ALLOW_METHOD = "GET"

    InputArgumentValidSet = [
        Argument('product-code', require=True, validtypes=['product']),
        Argument('unit', require=True, validtypes=['enum'], enum=['1M', '5M', '15M', '30M', '1H', '4H', '1D', '1W'],
                 defaultvalue='1M'),
        Argument('count', require=False, datatype=int, defaultvalue=10, validtypes=['range'],
                 range={'min': 0, 'max': 100}),
    ]

    def run(self):
        unit = self.InputArgument['unit']
        product_code = self.InputArgument['product-code']
        count = self.InputArgument['count']

        if self.check_product_code(product_code=product_code) is None:
            return self.Response(code='NOT_EXISTS_PRODUCT_CODE', status='BAD_REQUEST')

        sql = 'SELECT `time`,`open`,`high`,`low`,`close`,`volume` FROM `txquote`.`OHLC:{product_code}:{unit}` ORDER BY `time` DESC LIMIT %(count)s;'.format(
            product_code=product_code, unit=unit)
        kwargs = {
            'count': count
        }

        candle_list = list()
        if self.cur.execute(sql, kwargs):
            for time, open, high, low, close, volume in self.cur.fetchall():
                candles = dict()
                candles['timestamp'] = time
                candles['open'] = str(open)
                candles['high'] = str(high)
                candles['low'] = str(low)
                candles['close'] = str(close)
                candles['volume'] = str(volume)

                candle_list.append(candles)

        data = {
            "candles": candle_list,
        }
        self.con.commit()
        return self.Response(data=data)

    def check_product_code(self, product_code):
        """
        거래소 상품 목록들을 호출해 유저가 보낸 product_code 가 정상적인 상품코드인지 확인한다.
        """
        sql = 'SELECT `product_name` FROM `products`'

        if self.cur.execute(sql):
            product_codes = [product[0] for product in self.cur.fetchall()]
            if product_code in product_codes:
                return product_code
            else:
                return None

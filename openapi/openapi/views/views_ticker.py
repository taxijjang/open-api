from lib.ApiView import ApiView
import redis
from django.conf import settings
from lib.ApiView.Argument import Argument


class Ticker(ApiView):
    """
    거래소의 가상자산 현재가 정보를 제공한다.
    """
    DB_READONLY = True
    VERIFY_KEY = "APIKEY"
    ALLOW_METHOD = "GET"

    InputArgumentValidSet = [
        Argument('product-code', require=True, validtypes=['product']),
    ]

    def run(self):
        product_code = self.InputArgument['product-code']

        if self.check_product_code(product_code=product_code) is None:
            return self.Response(code='NOT_EXISTS_PRODUCT_CODE', status='BAD_REQUEST')

        product_name, min_size_unit, min_price_unit = self.get_items(product_code=product_code)

        data = {
            'trade_funds_24h': self.get_trade_funds24h(product_code=product_code),
            'trade_price': self.get_trade_price(product_code=product_code),
            'product_code': product_name,
            'min_size_unit': min_size_unit,
            'min_price_unit': min_price_unit,
        }
        self.con.commit()
        return self.Response(data=data)

    def get_trade_funds24h(self, product_code):
        """
        호출 당시 거래소의 24시간 이전 까지의 가상자산 거래량을 보여준다.
        """
        rcon = redis.Redis(**settings.RESPONSE_DB)
        name = 'TRADEFUNDS:{product_code}'.format(product_code=product_code)
        items = rcon.zrange(
            name=name,
            start=0,
            end=-1,
            withscores=True,
        )

        trade_funds = sum([int(v) for (k, v) in items])
        trade_funds_24h = float(trade_funds) / 10 ** 8
        return str(trade_funds_24h)

    def get_trade_price(self, product_code):
        """
        호출 당시 거래소 해당 가상자산의 현재가를 보여준다.
        """
        rcon = redis.Redis(**settings.RESPONSE_DB)
        name = 'TRADEPRICE:{product_code}'.format(product_code=product_code)
        trade_price = rcon.get(name)
        if trade_price is None:
            return 0.0
        else:
            trade_price = float(trade_price) / 10 ** 8
            return str(trade_price)

    def get_items(self, product_code):
        """
        상품명, 최소 수량, 최소 가격 등 거래소 거래를 위해 필요한 데이터를 제공한다.
        """
        sql = 'SELECT `product_name`, `min_size_unit`, `min_price_unit` FROM `products` WHERE `product_name`= %(product_name)s;'
        kwargs = {
            'product_name': product_code
        }
        if self.cur.execute(sql, kwargs):
            product_name, min_size_unit, min_price_unit = self.cur.fetchone()

            min_size_unit = float(min_size_unit) / 10 ** 8
            min_price_unit = float(min_price_unit) / 10 ** 8

            return product_name, str(min_size_unit), str(min_price_unit)

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

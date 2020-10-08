from lib.ApiView import ApiView
from django.conf import settings
import redis
import json


class TransactionHistory(ApiView):
    """
    체결 내역 API
    """
    VERIFY_KEY = "APIKEY"
    ALLOW_METHOD = "GET"

    def run(self):
        product_code, count = self.check_params

        if product_code is None:
            return self.Response(code='NOT_EXISTS_PRODUCT_CODE', status='BAD_REQUEST')

        datas = dict(
            transaction_history=list()
        )
        trade_historys = self.get_trade_history(product_code, count)

        for trade_history in trade_historys:
            trade_history = json.loads(trade_history)
            data = dict(
                product_code=trade_history['product'],
                price=str(trade_history['price']),
                size=str(trade_history['size']),
                timestamp=int(trade_history['time'] / 10 ** 6),
                side=trade_history['side'],
            )
            datas['transaction_history'].append(data)

        self.Response(data=datas)

    def get_trade_history(self, product_code, count):
        """

        redis db에서 해당 product_code의 trade_history 데이터를 가져온다.

        """
        rcon = redis.Redis(**settings.RESPONSE_DB)

        ### trade_history ###
        name = 'TRADEHISTORY:SNAPSHOT:{product_code}'.format(product_code=product_code)
        trade_history = rcon.zrevrange(name=name, start=0, end=count - 1, withscores=False, )

        return trade_history

    @property
    def check_params(self):
        """

        요청한 Query params가 올바르게 요청 되었는지 확인하는 부분

        """
        sql = 'SELECT `product_name` FROM `products` WHERE `product_status` = 2; '

        product_code = self.request.GET.get('product_code')
        count = self.request.GET.get('count')

        self.cur.execute(sql)

        if product_code is None:
            product_code_list = [product[0] for product in self.cur.fetchall()]
            product_code = product_code_list[0]
        else:
            product_code_list = [product[0] for product in self.cur.fetchall()]
            if product_code not in product_code_list:
                product_code = None

        try:
            count = int(count)
            if count < 0 or count > 30:
                count = 10

        except:
            count = 10

        return product_code, count

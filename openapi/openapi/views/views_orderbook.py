from lib.ApiView import ApiView
import operator
import redis
import time
from django.conf import settings


class OrderBook(ApiView):
    VERIFY_KEY = "APIKEY"
    ALLOW_METHOD = "GET"

    def run(self):
        product_code, count = self.check_params

        if product_code is None:
            return self.Response(status='BAD_REQUEST', code='NOT_EXISTS_PRODUCT_CODE')

        product_name, min_size_unit, min_price_unit, digit = self.get_product_data(product_code=product_code)

        order_book_ask, order_book_bid = self.get_order_book(
            product_code=product_code,
            count=count,
            digit=digit

        )

        data = dict(
            timestamp=int(time.time()),
            product_code=product_code,
            bid=order_book_bid,
            ask=order_book_ask,
            min_size_unit=min_size_unit,
            min_price_unit=min_price_unit,
        )

        self.con.commit()
        return self.Response(data=data)

    def get_order_book(self, product_code, count, digit):
        """
        redis db에서 해당 prodcut_code의 order_book 데이터를 가져온다.

        """
        rcon = redis.Redis(**settings.RESPONSE_DB)

        ### order_book_ask ###
        order_book_ask = rcon.zrange(name="ORDERBOOK:{product_code}:ASK".format(product_code=product_code),
                                     start=0,
                                     end=-1,
                                     withscores=True)
        order_book_ask = list(((float(price) / (10 ** digit)), size / (10 ** digit)) for price, size in order_book_ask)
        order_book_ask.sort(key=operator.itemgetter(0))
        order_book_ask = list(dict(price=str(price), size=str(size)) for price, size in order_book_ask)
        order_book_ask = order_book_ask[0:count]

        ### order_book_bid ###
        order_book_bid = rcon.zrange(name="ORDERBOOK:{product_code}:BID".format(product_code=product_code),
                                     start=0,
                                     end=-1,
                                     withscores=True)
        order_book_bid = list(((float(price) / (10 ** digit)), size / (10 ** digit)) for price, size in order_book_bid)
        order_book_bid.sort(key=operator.itemgetter(0))
        order_book_bid = list(dict(price=str(price), size=str(size)) for price, size in order_book_bid)
        order_book_bid = order_book_bid[0:int(count)]

        return order_book_ask, order_book_bid

    def get_product_data(self, product_code):
        """
        해당 product_code에 대한 여러 데이터를 가져온다.
        ex) min_size_unit, min_price_unit

        """
        sql = "SELECT `a`.`product_name`, `a`.`min_size_unit`, `a`.`min_price_unit`, `b`.`digit` FROM `products` AS `a`" \
              "LEFT JOIN `currency` AS `b` ON `a`.`base_currency_code` = `b`.`code`" \
              "WHERE `a`.`product_name` = %(product_code)s ;"

        kwagrs = dict(
            product_code=product_code
        )
        if self.cur.execute(sql, kwagrs):
            product_name, min_size_unit, min_price_unit, digit = self.cur.fetchone()

            min_size_unit = float(min_size_unit) / 10 ** digit
            min_price_unit = float(min_price_unit) / 10 ** digit

            return product_name, str(min_size_unit), str(min_price_unit), int(digit)

    @property
    def check_params(self):
        """
        요청한 Query params가 올바르게 요청 되었는지 확인하는 부분
        :return:
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
            if count < 0:
                count = 30
        except:
            count = 30

        return product_code, count

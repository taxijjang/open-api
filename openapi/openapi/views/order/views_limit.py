from __future__ import unicode_literals

import lib.define
from lib.libTools import cached_property
from lib.ApiView import ApiView
from lib.ApiView.Argument import Argument
from lib import define
from django.core.cache import cache

class OrderLimitSend(ApiView):
    VERIFY_KEY = "SECRETKEY"
    ALLOW_METHOD = "POST"
    DB_READONLY = True
    FUNC_CHECK_TRADE = True

    InputArgumentValidSet = [
        Argument('product_code', require=True, validtypes=['product']),
        Argument('price', datatype=float, validtypes=['float_nonzero']),
        Argument('side', validtypes=['enum'], enum=['BUY', 'SELL']),
        Argument('size', datatype=float, validtypes=['float_nonzero']),
        Argument('magicnumber', require=False, datatype=int, validtypes=['range'], defaultvalue=0,
                 range={'min': 0, 'max': 2 ** 32}),
    ]

    def run(self):
        """
        TODO : stop_price , size, price 소수점도 입력이 되므로 정수로 변환해주도록 APIView lib 안에서 처리하도록 해야될듯
        :return:
        """
        # 상품 체크
        if self.product is None:
            return self.Response(status='BAD_REQUEST',code="NOT_EXISTS_PRODUCT_CODE")

        ## 거래 가능 여부 체크
        if not self.check_is_trade:
            return self.Response(status='BAD_REQUEST',code='NOT_ALLOW_PRODUCT_ORDER_TYPE')

        ## 거래 가능 여부 체크
        if not self.check_is_trade:
            return self.Response(status='BAD_REQUEST', code='NOT_ALLOW_PRODUCT_ORDER_TYPE')

        ## 소수점으로 입력받은 price 정수로 변환
        self.InputArgument['price'] = int(round(self.InputArgument['price'] * 10 ** self.product['digit'], 0))

        # price 체크
        abandon_price = self.InputArgument['price'] % self.product['min_price_unit']
        price = self.InputArgument['price'] - abandon_price
        if price <= 0:
            return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_PRICE')

        ## 소수점으로 입력받은 size 정수로 변환

        self.InputArgument['size'] = int(round(self.InputArgument['size'] * 10 ** self.product['digit'], 0))

        # size 체크
        abandon_size = self.InputArgument['size'] % self.product['min_size_unit']
        size = self.InputArgument['size'] - abandon_size

        if size <= 0:
            return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_SIZE')

        self.member.OrderSend.limit_gtc(
            product_code=self.product['product_code'],
            side=self.InputArgument['side'],
            price=price,
            size=size,
            magicnumber=self.InputArgument['magicnumber'],
        )
        abandon_price = round(abandon_price / self.product['min_price_unit'], self.round_count)
        abandon_size = round(abandon_size / self.product['min_size_unit'], self.round_count)

        order_size = size / (10 ** self.product['digit'])
        order_price = price / (10 ** self.product['digit'])

        data = dict(
            order_price=str(order_price),
            order_size=str(order_size),
        )

        self.con.commit()
        return self.Response(data=data)

    @cached_property
    def product(self):
        """
        product_status : 1:비상장, 2:상장, 2:폐지
        """

        sql = "SELECT " \
              "`p`.`product_id` AS `product_id`," \
              "`p`.`product_name` AS `product_code`, " \
              "`p`.`min_price_unit`, " \
              "`p`.`min_size_unit`, " \
              "`qc`.`digit` " \
              "FROM `products` AS `p` " \
              "LEFT JOIN `currency` AS `qc` ON `p`.`quote_currency_id`=`qc`.`id` " \
              "WHERE `p`.`product_name`=%(product_code)s AND `p`.`product_status`=2;"

        kwargs = {
            "product_code": self.InputArgument['product_code'],
        }

        if self.cur.execute(sql, kwargs):
            return self.cur.fetchone(with_keys=True)
        else:
            return None

    @cached_property
    def check_is_trade(self):
        """

        거래 가능한 product인지 확인
        
        """

        sql = "SELECT 1 FROM `products_trade_deny` WHERE `product_id`=%(product_id)s " \
              "AND `order_type` IN %(order_types)s;"
        kwagrs = {
            "product_id": self.product['product_id'],
            "order_types": (define.ORDER_TYPE['LIMIT'], define.ORDER_TYPE['MARKET']),
        }

        if self.cur.execute(sql, kwagrs):
            return False
        else:
            return True

    @cached_property
    def round_count(self):
        zero = list(str(self.product['min_price_unit']))
        zero_cnt = len(zero)

        return abs(self.product['digit'] - zero_cnt - 1)

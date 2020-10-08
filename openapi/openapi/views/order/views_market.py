from lib.ApiView import ApiView
from lib.ApiView.Argument import Argument
from lib.libTools import cached_property
from lib import define


class OrderMarketSend(ApiView):
    VERIFY_KEY = "SECRETKEY"
    ALLOW_METHOD = "POST"
    DB_READONLY = True
    FUNC_CHECK_TRADE = True

    InputArgumentValidSet = [
        Argument('product_code', require=True, validtypes=['product']),
        Argument('side', require=True, validtypes=['enum'], enum=['BUY', 'SELL']),
        Argument('size', require=True, datatype=float, validtypes=['float_nonzero']),
        Argument('magicnumber', require=False, datatype=int, validtypes=['range'], defaultvalue=0,
                 range={'min': 0, 'max': 2 ** 32}),
    ]

    def run(self):
        ## 상품 체크
        if self.product is None:
            return self.Response(status='BAD_REQUEST', code="NOT_EXISTS_PRODUCT_CODE")

        ## 거래 가능 여부 체크
        if not self.check_is_trade:
            return self.Response(status='BAD_REQUEST', code='NOT_ALLOW_PRODUCT_ORDER_TYPE')

        ## 소수점으로 입력받은 size 정수로 변환
        self.InputArgument['size'] = int(round(self.InputArgument['size'] * 10 ** self.product['digit'], 0))

        ## BUY
        if self.InputArgument['side'] == 'BUY':
            if self.product['min_trade_funds'] > 0:
                if self.InputArgument['size'] < self.product['min_trade_funds']:
                    return self.Response(status='BAD_REQUEST', code="INVALID_MIN_TRADE_FUNDS")

            self.member.OrderSend.market_buy(
                product_code=self.product['product_code'],
                funds=self.InputArgument['size'],
                magicnumber=self.InputArgument['magicnumber'],
            )

            order_funds = self.InputArgument['size'] / (10 ** self.product['digit'])

            data = dict(
                order_funds=str(order_funds),
            )


        ## SELL
        else:
            abandon_size = self.InputArgument['size'] % self.product['min_size_unit']
            size = self.InputArgument['size'] - abandon_size

            if size <= 0:
                return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_SIZE')

            self.member.OrderSend.market_sell(
                product_code=self.product['product_code'],
                size=size,
                magicnumber=self.InputArgument['magicnumber'],
            )

            order_size = size / (10 ** self.product['digit'])

            data = dict(
                order_size=str(order_size),
            )

        self.con.commit()
        return self.Response(data=data)

    @cached_property
    def product(self):
        """
        product_status : 1:비상장, 2:상장, 3:폐지
        """
        print("##### IN product #####")
        sql = "SELECT " \
              "`p`.`product_id` AS `product_id`," \
              "`p`.`product_name` AS `product_code`, " \
              "`qc`.`min_trade_funds`, " \
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

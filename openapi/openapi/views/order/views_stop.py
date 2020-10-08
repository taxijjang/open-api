from lib.ApiView import ApiView
from lib.ApiView.Argument import Argument
from lib.libTools import cached_property
import lib.define


class StopOrderView(ApiView):
    VERIFY_KEY = 'SECRETKEY'
    ALLOW_METHOD = "POST"
    DB_READONLY = True
    FUNC_CHECK_TRADE = True

    InputArgumentValidSet = [
        Argument('product_code', require=True, validtypes=['product']),
        Argument('stop_price', datatype=float, validtypes=['float_nonzero']),
        Argument('price', require=False, datatype=float, validtypes=['float_nonzero']),
        Argument('side', validtypes=['enum'], castings=['upper'], enum=['BUY', 'SELL']),
        Argument('size', require=True, datatype=float, validtypes=['float_nonzero']),
        Argument('magicnumber', require=False, datatype=int, validtypes=['range'], range={'min': 0, 'max': 2 ** 32}),
    ]

    def previous_run(self):
        # 상품 체크
        if self.product is None:
            return self.Response(code='NOT_EXISTS_PRODUCT_CODE')

    def run(self):
        size = int(round(self.InputArgument['size'] * (10 ** 8), 0))
        if self.InputArgument['price'] is not None:
            price = int(round(self.InputArgument['price'] * (10 ** 8), 0))
        stop_price = int(round(self.InputArgument['stop_price'] * (10 ** 8), 0))

        if self.InputArgument['price'] is None:
            try:
                stop_price, size = self.stop_market(stop_price=stop_price, size=size)
                data = {
                    "order_stop_price": str(stop_price / 10 ** 8),
                }
                if self.InputArgument['side'] == 'BUY':
                    data.update({'order_funds': str(size / 10 ** 8)})
                else:
                    data.update({'order_size': str(size / 10 ** 8)})

                return self.Response(data=data)

            except NotAllowProductOrderTypeError:
                return self.Response(status='BAD_REQUEST', code='NOT_ALLOW_PRODUCT_ORDER_TYPE')
            except InvalidStopPriceError:
                return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_PRICE')
            except InvalidMinTradeFundsError:
                return self.Response(status='BAD_REQUEST', code='INVALID_MIN_TRADE_FUNDS')
            except InvalidTradeSizeError:
                return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_SIZE')
        else:
            try:
                price, stop_price, size = self.stop_limit(stop_price=stop_price, price=price, size=size)
                data = {
                    'order_price': str(price / 10 ** 8),
                    'order_stop_price': str(stop_price / 10 ** 8),
                    'order_size': str(size / 10 ** 8),
                }
                return self.Response(data=data)

            except NotAllowProductOrderTypeError:
                return self.Response(status='BAD_REQUEST', code='NOT_ALLOW_PRODUCT_ORDER_TYPE')
            except InvalidStopPriceError:
                return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_PRICE')
            except InvalidTradePriceError:
                return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_PRICE')
            except InvalidTradeSizeError:
                return self.Response(status='BAD_REQUEST', code='INVALID_TRADE_SIZE')

        self.con.commit()
        return self.Response()

    def stop_market(self, stop_price, size):
        # 거래 가능 여부 체크
        if not self.is_trade_market:
            raise NotAllowProductOrderTypeError()

        # min_stop_price 체크
        new_stop_price = stop_price - stop_price % self.product[
            'min_price_unit']
        if new_stop_price <= 0:
            raise InvalidStopPriceError()

        if self.InputArgument['side'] == 'BUY':  # Market Buy(Funds)
            if self.product['min_trade_funds'] > 0:
                if size < self.product['min_trade_funds']:
                    raise InvalidMinTradeFundsError()

            self.member.OrderSend.stop_market_buy(
                product_code=self.product['code'],
                stop_price=new_stop_price,
                funds=size,
                magicnumber=self.InputArgument['magicnumber'],
            )
            return stop_price, size
        elif self.InputArgument['side'] == 'SELL':  # Market Sell(Size)
            new_size = size - size % self.product['min_size_unit']
            if new_size <= 0:
                raise InvalidTradeSizeError()

            self.member.OrderSend.stop_market_sell(
                product_code=self.product['code'],
                stop_price=new_stop_price,
                size=new_size,
                magicnumber=self.InputArgument['magicnumber'],
            )
            return stop_price, size

    def stop_limit(self, stop_price, price, size):
        # 거래 가능 여부 체크
        if not self.is_trade_limit:
            raise NotAllowProductOrderTypeError()

        new_stop_price = stop_price - stop_price % self.product[
            'min_price_unit']
        if new_stop_price <= 0:
            raise InvalidStopPriceError()

        # min_price_unit 체크
        new_price = price - price % self.product['min_price_unit']
        if new_price <= 0:
            raise InvalidTradePriceError()

        # min_size_unit 체크
        new_size = size - size % self.product['min_size_unit']
        if new_size <= 0:
            raise InvalidTradeSizeError()

        self.member.OrderSend.stop_limit(
            product_code=self.product['code'],
            side=self.InputArgument['side'],
            stop_price=new_stop_price,
            price=new_price,
            size=new_size,
            magicnumber=self.InputArgument['magicnumber'],
        )
        return new_price, new_stop_price, size

    @cached_property
    def product(self):
        """
        product_status : 1:비상장, 2:상장, 2:폐지
        """
        sql = "SELECT " \
              "`p`.`product_id` AS `id`," \
              "`p`.`product_name` AS `code`, " \
              "`p`.`min_price_unit`, " \
              "`p`.`min_size_unit`, " \
              "`qc`.`min_trade_funds` " \
              "FROM `products` AS `p` " \
              "LEFT JOIN `currency` AS `qc` ON `p`.`quote_currency_id`=`qc`.`id` " \
              "WHERE `p`.`product_name`=%s AND `p`.`product_status`=2;"
        if self.cur.execute(sql, self.InputArgument['product_code']):
            return self.cur.fetchone(with_keys=True)
        else:
            return None

    @cached_property
    def is_trade_limit(self):
        sql = "SELECT 1 FROM `products_trade_deny` " \
              "WHERE `product_id`=%(product_id)s " \
              "AND `order_type` IN %(order_types)s;"
        kwargs = {
            'product_id': self.product['id'],
            'order_types': (lib.define.ORDER_TYPE['LIMIT'], lib.define.ORDER_TYPE['STOP']),
        }
        if self.cur.execute(sql, kwargs):
            return False
        else:
            return True

    @cached_property
    def is_trade_market(self):
        sql = "SELECT 1 FROM `products_trade_deny` " \
              "WHERE `product_id`=%(product_id)s " \
              "AND `order_type` IN %(order_types)s;"
        kwargs = {
            'product_id': self.product['id'],
            'order_types': (
                lib.define.ORDER_TYPE['LIMIT'], lib.define.ORDER_TYPE['MARKET'], lib.define.ORDER_TYPE['STOP']),
        }
        if self.cur.execute(sql, kwargs):
            return False
        else:
            return True


class InvalidStopPriceError(Exception):
    pass


class InvalidTradePriceError(Exception):
    pass


class InvalidTradeSizeError(Exception):
    pass


class NotAllowProductOrderTypeError(Exception):
    pass


class InvalidMinTradeFundsError(Exception):
    pass

from lib.ApiView import ApiView
from lib import define
from lib.ApiView.Argument import Argument


class TradeHistory(ApiView):
    """
    회원 거래내역 API
    """
    DB_READONLY = True
    VERIFY_KEY = 'SECRETKEY'
    ALLOW_METHOD = "GET"

    InputArgumentValidSet = [
        Argument('product-code-list', require=True),
        Argument('order-type', require=False, validtypes=['enum'], enum=['MARKET', 'LIMIT'], defaultvalue='LIMIT'),
        Argument('side', require=False, validtypes=['enum'], enum=['BUY', 'SELL', 'ALL'], defaultvalue='ALL'),
        Argument('count', require=False, datatype=int, defaultvalue=10, validtypes=['range'],
                 range={'min': 0, 'max': 100}),
        Argument('magicnumber', require=False, datatype=int, validtypes=['range'], defaultvalue=0,
                 range={'min': 0, 'max': 2 ** 32}),
    ]

    def run(self):
        order_type = self.InputArgument['order-type']
        product_code_list = self.InputArgument['product-code-list'].split(',')
        side = self.InputArgument['side']
        count = self.InputArgument['count']
        magic_number = self.InputArgument['magicnumber']

        try:
            trans_side = define.ORDER_HISTORY_TYPE[side]
        except KeyError:
            return self.Response(code='NOT_EXISTS_SIDE', status='BAD_REQUEST')

        try:
            trans_order_type = define.ORDER_HISTORY_TYPE[order_type]
        except KeyError:
            return self.Response(code='NOT_EXISTS_ORDER_TYPE', status='BAD_REQUEST')

        product_code_list = self.check_product_code(product_code_list=product_code_list)
        if product_code_list is None:
            return self.Response(code='NOT_EXISTS_PRODUCT_CODE', status='BAD_REQUEST')

        sql = "SELECT `order_id`, `done_time`, `product`, " \
              "`open_price`, `accumulate_size`, `accumulate_fee`, " \
              "`accumulate_funds`, `bcc`, `qcc`, `bcd`, `qcd`, `magicnumber`, `side` FROM `order:DONE` " \
              "WHERE `member_id`=%(member_id)s AND " \
              "`side` IN %(side)s AND " \
              "`product` IN %(product_code_list)s " \
              "AND `order_type`= %(order_type)s " \
              "AND `magicnumber`= %(magic_number)s  ORDER BY `seq` DESC LIMIT %(count)s;"
        kwargs = {
            'member_id': self.secret_key.member_id,
            'side': trans_side,
            'product_code_list': product_code_list,
            'order_type': trans_order_type,
            'count': count,
            'magic_number': 0 if magic_number is None else magic_number,
        }

        data = {
            "trade_list": list()
        }

        if self.cur.execute(sql, kwargs):
            for order_id, done_time, product, open_price, accumulate_size, accumulate_fee, accumulate_funds, bcc, qcc, bcd, qcd, magic_number, side in self.cur.fetchall():
                order = dict()
                order['order_id'] = order_id
                order['done_time'] = int(done_time / 10 ** 6)
                order['product'] = product
                order['side'] = None if side is None else define.pSIDE[side]
                order['order_type'] = order_type
                order['price'] = '0' if open_price is None else str(open_price / 10 ** bcd)
                order['size'] = str(accumulate_size / 10 ** qcd)
                order['fee'] = str(accumulate_fee / 10 ** bcd)
                order['total_price'] = str(accumulate_funds / 10 ** bcd)
                order['base_currency_code'] = bcc
                order['quote_currency_code'] = qcc
                order['magic_number'] = magic_number

                data['trade_list'].append(order)
        self.con.commit()
        return self.Response(data=data)

    def check_product_code(self, product_code_list):
        """
        거래소 상품 목록들을 호출해 유저가 보낸 product_code 가 정상적인 상품코드인지 확인한다.
        """
        sql = 'SELECT `product_name` FROM `products`'

        if self.cur.execute(sql):
            product_codes = [product[0] for product in self.cur.fetchall()]
            for product_code in product_code_list:
                if product_code not in product_codes:
                    return None

        return product_code_list

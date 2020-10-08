from lib.ApiView import ApiView
from lib import define

class OrderHistory(ApiView):
    """
    주문내역 API
    """
    VERIFY_KEY = "SECRETKEY"
    ALLOW_METHOD = "GET"

    def run(self):
        order_id = self.order_id_check
        if order_id is None:
            return self.Response(status='BAD_REQUEST',code='NOT_EXISTS_ORDER_ID')

        stop_order = self.get_stop_order(order_id)
        if stop_order is None:
            product_code_and_magicnumber = self.get_product_code_by_order_id(order_id)

            if product_code_and_magicnumber is not None:
                product_code, magicnumber = product_code_and_magicnumber

                order_history = self.get_orderhistory(product_code=product_code, order_id=order_id)

                data = dict(
                    stop_price=str(0 if order_history['stop_price'] is None else order_history['stop_price']),
                    order_type=define.pORDER_TYPE[order_history['order_type']],
                    price=str(0 if order_history['price'] is None else order_history['price'] / (10 ** order_history['bcd'])),
                    base_currency_code=order_history['bcc'],
                    quote_currency_code=order_history['qcc'],
                    size=str(0 if order_history['amount'] is None else order_history['amount'] / 10 ** 8),
                    timestamp=int(order_history['time']/ 10 ** 6),
                    side=define.pSIDE[order_history['side']],
                    magicnumber=magicnumber,
                )

                self.con.commit()
                return self.Response(data=data)

        else:
            data = dict(
                stop_price=str(0 if stop_order['stop_price'] is None else stop_order['stop_price'] / 10 ** stop_order['qcd']),
                price=str(0 if stop_order['price'] is None else stop_order['price'] / 10 ** stop_order['qcd']),
                order_type="STOP",
                base_currency_code=stop_order['bcc'],
                quote_currency_code=stop_order['qcc'],
                size=str(0 if stop_order['size'] is None else stop_order['size'] / 10 ** stop_order['bcd']),
                timestamp=int(stop_order['time'] / 10 ** 6),
                side=define.pSIDE[stop_order['side']],
            )
            self.con.commit()
            return self.Response(data=data)

        self.con.commit()
        return self.Response(status='BAD_REQUEST',code="NOT_EXISTS_ORDER_ID")

    def get_stop_order(self, order_id):
        """

        (member_id,order_id) 가 예약주문에 현재 있는지 확인

        """
        sql = "SELECT `member_id`, `stop_price`, `price`, `bcc`, `qcc`,`bcd`,`qcd`,`size`, `time`, `side` FROM `order:STOP` " \
              "WHERE `order_id` = %(order_id)s AND `member_id` = %(member_id)s; "
        kwargs = {
            "order_id": order_id,
            "member_id": self.secret_key.member_id,
        }

        if self.cur.execute(sql, kwargs) is None:
            return None
        else:
            return self.cur.fetchone(with_keys=True)

    def get_product_code_by_order_id(self, order_id):
        """

        (member_id, order_id) 가 예약주문에 없기 때문에
        order:DONE과 order:OPEN에서 order_id 검색

        """

        sql = "SELECT `product`, `magicnumber` FROM `order:DONE` WHERE `order_id` = %(order_id1)s AND `member_id` = %(member_id1)s" \
              "UNION SELECT `product`,`magicnumber` FROM `order:OPEN` WHERE `order_id` = %(order_id2)s AND `member_id` = %(member_id2)s; "

        kwargs = {
            "order_id1": order_id,
            "member_id1": self.secret_key.member_id,
            "order_id2": order_id,
            "member_id2": self.secret_key.member_id,
        }
        self.cur.execute(sql, kwargs)

        product_code = self.cur.fetchone()

        return product_code

    def get_orderhistory(self, product_code, order_id):
        """

        사용자의 주문 내역 출력

        """

        sql = "SELECT `stop_price`, `history_type`, `order_type`, `price`, `bcc`, `qcc`,`bcd`,`qcd`, `amount`, `time`, `side` FROM `{product_code}:order:HISTORY`" \
              "WHERE `order_id` = %(order_id)s ORDER BY `identity` DESC; ".format(product_code=product_code)

        kwargs = {
            "order_id": order_id,
        }
        self.cur.execute(sql, kwargs)

        order_history = self.cur.fetchone(with_keys=True)

        return order_history


    @property
    def order_id_check(self):
        """

        유효한 order_id 인지 확인
        TODO: 현재는 order_id의 길이만을 이용하여 체크하고있음
            : db를 뒤져서 order_id가 맞는지 확인 하는 작업은 뭔가 비효율적인거 같음..
       """
        order_id = self.request.GET.get("order_id")

        if order_id is None or len(order_id) != 36:
            return None

        return order_id

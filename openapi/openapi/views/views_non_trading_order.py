from lib.ApiView import ApiView
from lib.libTools import cached_property
from lib import define


class NonTradingOrder(ApiView):
    VERIFY_KEY = "SECRETKEY"
    ALLOW_METHOD = "GET"

    def run(self):

        order_stop = list()
        order_open = list()

        for order in self.order_open:
            order_data = dict(
                order_id=order['order_id'],
                time=int(order['open_time'] / (10 ** 6)),
                product_code=order['product'],
                side=define.pSIDE[order['side']],
                stop_order=define.pSTOP_ORDER[order['stoporder']],
                order_type=define.pORDER_TYPE[order['order_type']],
                price=str(0 if order['price'] is None else order['price'] / (10 ** order['qcd'])),
                size=str(0 if order['size'] is None else order['size'] / (10 ** order['bcd'])),
                remaining_size=(0 if order['remaining_size'] is None else order['remaining_size'] / (10 ** order['bcd'])),
                magicnumber=order['magicnumber'],
            )

            order_open.append(order_data)

        for order in self.order_stop:
            order_data = dict(
                order_id=order['order_id'],
                time=int(order['time'] / 10 ** 6),
                product_code=order['product'],
                side=define.pSIDE[order['side']],
                order_type=define.pORDER_TYPE[order['order_type']],
                price=str(0 if order['price'] is None else order['price'] / (10 ** order['qcd'])),
                size=str(0 if order['size'] is None else order['size'] / (10 ** order['bcd'])),
                funds=str(0 if order['funds'] is None else order['funds'] / (10 ** order['qcd'])),
            )
            order_stop.append(order_data)

        data = dict(
            order_stop=order_stop,
            order_open=order_open,
        )

        return self.Response(data=data)

    @cached_property
    def order_stop(self):
        sql = "SELECT `order_id`, `time`, `product`, `side`, `order_type`, `stop_price`, `price`, `size`, " \
              "`funds`, `bcd`,`qcd` FROM `order:STOP` WHERE `member_id` = %(member_id)s ORDER BY `time` DESC; "

        kwargs = dict(
            member_id=self.secret_key.member_id,
        )

        self.cur.execute(sql, kwargs)
        return self.cur.fetchall(with_keys=True)

    @cached_property
    def order_open(self):
        sql = "SELECT `order_id`, `product`, `product`, `side`, `size`,`price`, `remaining_size`, " \
              "`magicnumber`,`stoporder`,`bcd`,`qcd`,`open_time`, `order_type`   FROM `order:OPEN`" \
              " WHERE `member_id` = %(member_id)s ORDER BY `open_time` DESC; "

        kwargs = dict(
            member_id=self.secret_key.member_id,
        )
        self.cur.execute(sql, kwargs)
        return self.cur.fetchall(with_keys=True)

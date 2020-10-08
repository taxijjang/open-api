from __future__ import unicode_literals

from lib.libTools import cached_property
from lib.ApiView import ApiView
from lib.ApiView.Argument import Argument


class OrderCancelSend(ApiView):
    VERIFY_KEY = "SECRETKEY"
    ALLOW_METHOD = "POST"
    DB_READONLY = True
    FUNC_CHECK_TRADE = True

    InputArgumentValidSet = [
        Argument('order_id', validtypes=['uuid']),
    ]

    def run(self):
        if self.cancelorder is None:
            return self.Response(status='BAD_REQUEST', code='NOT_EXISTS_ORDER_ID')

        self.member.OrderSend.cancel(
            product_code=self.cancelorder['product_code'],
            order_id=self.InputArgument['order_id'],
        )

        self.con.commit()
        return self.Response(data=None)

    @cached_property
    def cancelorder(self):
        print(self.secret_key.member_id)
        sql = "SELECT `order_id`, `product` AS `product_code` FROM `order:OPEN`" \
              "WHERE `member_id`=%(member_id)s AND `order_id`=%(order_id)s;"
        kwargs = {
            'member_id': self.secret_key.member_id,
            'order_id': self.InputArgument['order_id'],
        }
        if self.cur.execute(sql, kwargs):
            return self.cur.fetchone(with_keys=True)
        else:
            return None


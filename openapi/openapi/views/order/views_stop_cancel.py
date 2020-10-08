from lib.ApiView import ApiView
from lib.ApiView.Argument import Argument

class StopOrderCancelView(ApiView):
    VERIFY_KEY = 'SECRETKEY'
    ALLOW_METHOD = "POST"
    DB_READONLY = True
    FUNC_CHECK_TRADE = True

    InputArgumentValidSet = [
        Argument('order_id', validtypes=['uuid']),
    ]

    def run(self):
        sql = "SELECT `product` FROM `order:STOP` WHERE `member_id`=%(member_id)s AND `order_id`=%(order_id)s;"
        kwargs = {'member_id': self.member.member_id, 'order_id': self.InputArgument['order_id']}
        if not self.cur.execute(sql, kwargs):
            return self.Response(status='BAD_REQUEST', code='NOT_EXISTS_ORDER_ID')

        product_code = self.cur.fetchone()[0]
        self.member.OrderSend.stopcancel(
            product_code=product_code,
            order_id=self.InputArgument['order_id'],
        )
        self.con.commit()
        return self.Response()
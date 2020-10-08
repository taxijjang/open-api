from lib.libTools import cached_property
from . import (
    MemStatus,
    OrderSend,
)
from .. import exceptions


class MemberProperty:
    def __init__(self, name):
        self.name = name

    def __set__(self, instance, value):
        error = "'{class_name}' object attribute '{name}' is read-only".format(
            class_name=instance.__class__.__name__,
            name=self.name,
        )
        raise AttributeError(error)

    def __get__(self, instance, owner):
        return instance.memberinfo[self.name]


class Member:
    wallet_id = MemberProperty('wallet_id')
    authgrade = MemberProperty('authgrade')

    def __init__(self, cursor, member_id):
        self.cur = cursor
        self.member_id = member_id

        self.OrderSend = OrderSend.OrderSend(self.cur, self)  # 해당 사용자 주문 날리기

    @cached_property
    def memberinfo(self):
        sql = "SELECT * FROM `member` WHERE `member_id`=%s;"
        if self.member_id is not None and self.cur.execute(sql, (self.member_id,)):
            return self.cur.fetchone(with_keys=True)
        raise exceptions.NotFoundMemberIdError(self.member_id)

    @cached_property
    def memstatus(self):
        """memstatus에 따른 기능을 가져오기 위하여 memstatus는 별도의 class로 처리함"""
        return MemStatus.MemStatus(self.cur, self.memberinfo['memstatus'])

    @cached_property
    def fee_rate(self):
        def default_fee_rate():
            sql = "SELECT `tfr`,`mfr` FROM `mem_feerate` WHERE `grade`=1;"
            self.cur.execute(sql)
            return self.cur.fetchone(with_keys=True)

        if self.member_id is None:
            return default_fee_rate()
        else:
            sql = "SELECT `tfr`,`mfr` FROM `mem_feerate_relation` WHERE `member_id`=%s;"
            if self.cur.execute(sql, (self.member_id,)):
                return self.cur.fetchone(with_keys=True)
            else:
                return default_fee_rate()

from . import exceptions
from lib.Exchange.Member import Member

class KeyBase:
    kind = None

    def __init__(self, cursor, api_key=None, secret_key=None):
        self.cur = cursor
        self.api_key = api_key
        self.secret_key = secret_key
        self.is_verify = False
        self.verify_payload = None

    def verify(self):
        payload = self.find_key(kind=self.kind, api_key=self.api_key, secret_key=self.secret_key)

        if payload is None:
            raise exceptions.InvalidKeyError
        if not payload[0]:
            raise exceptions.NotVerifyKeyError

        self.is_verify = True
        self.verify_payload = payload

    def find_key(self, kind, api_key, secret_key):
        if kind == 'APIKEY':
            sql = "SELECT `member_id` FROM `mem_api_key` WHERE `api_key` = %(api_key)s"
            kwargs = {
                "api_key": api_key
            }
            if self.cur.execute(sql, kwargs):
                return self.cur.fetchone()
            else:
                return None
        elif kind == 'SECRETKEY':
            sql = "SELECT `member_id` FROM `mem_api_key` WHERE `api_key` = %(api_key)s AND `secret_key`= %(secret_key)s"
            kwargs = {
                "api_key": api_key,
                "secret_key": secret_key,
            }
            if self.cur.execute(sql, kwargs):
                return self.cur.fetchone()
            else:
                return None
        else:
            return None


class ApiKey(KeyBase):
    kind = 'APIKEY'


class SecretKey(KeyBase):
    kind = 'SECRETKEY'

    @property
    def payload(self):
        if self.verify_payload is None:
            raise exceptions.NotVerifyKeyError
        else:
            return self.verify_payload

    @property
    def member_id(self):
        if self.payload[0] is not None:
            return self.payload[0]
        else:
            raise exceptions.InvalidKeyError

    @property
    def trade(self):
        member = Member(self.cur, self.member_id)
        return member.memstatus.trade

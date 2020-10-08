from lib.ApiView import ApiView
import requests
from django.conf import settings
import json
from urllib.parse import urlencode
from lib.ApiView.Argument import Argument
from lib import define


class Assets(ApiView):
    """
    회원 자산을 보여주는 API
    """
    DB_READONLY = True
    VERIFY_KEY = 'SECRETKEY'
    ALLOW_METHOD = "GET"

    InputArgumentValidSet = [
        Argument('currency-code-list', require=True),
    ]

    def run(self):
        """
        회원이 요청한 currency_code 들을 기준으로 회원이 보유한 자산이 호출되며,
        거래소 Asset 서버로 회원 자산을 요청 한다.
        """
        currency_codes = dict()
        currency_code_list = self.InputArgument['currency-code-list'].split(',')

        for currency_code in currency_code_list:
            if self.cur.execute('SELECT `id`, `code` FROM `currency` WHERE `code` = %(code)s', {'code': currency_code}):
                _, currency_code = self.cur.fetchone()
                currency_codes[currency_code] = currency_code
            else:
                self.Response(code='NOT_EXISTS_CURRENCY_ID', status='BAD_REQUEST')
                return

        r, display_currency = self.get_display_currency

        if not r:
            self.con.rollback()
            self.Response(status='BAD_REQUEST', code='NOT_EXISTS_DSP_CURRENCY_ID')
            return

        # wallet_id
        r = requests.get(settings.WALLETAPI_BASEURL + '/assets' + '?' + urlencode(
            {'wallet_id': self.member.wallet_id, 'dsp_currency_code': display_currency['code'],
             'currency_codes': ','.join(currency_codes.keys())}))

        response = json.loads(r.text)
        if response['response_code'] == 0:
            data = dict()
            data['dsp_currency'] = display_currency['code']
            data['assets'] = dict()
            for key, value in response['data'].items():
                if key == 'dsp_currency_code':
                    continue
                data['assets'][key] = {
                    'currency_code': key,
                    'balance': str(float(value['balance']) / 10 ** 8),
                    'hold': str(float(value['hold']) / 10 ** 8),
                    'avg_price': str(float(value['avgp']) / 10 ** 8),
                    'accum_deposit': str(float(value['accumdeposit']) / 10 ** 8),
                    'accum_withdraw': str(float(value['accumwithdraw']) / 10 ** 8),
                }
            self.con.commit()
            self.Response(data=data)
        else:
            raise ValueError('UNKNOWN')

    @property
    def get_display_currency(self):
        """
        회원의 자산 기준 코인을 검증 하며, 회원에게 별도로 설정된 자산 기준 코인이 등록되있지 않을때,
        거래소 기본 자산 기준 코인으로 설정.
        """
        if self.cur.execute("SELECT `display_currency_id` FROM `mem_config` WHERE `member_id`=%(member_id)s;",
                            {'member_id': self.secret_key.member_id}):
            display_currency_id, = self.cur.fetchone()
        else:
            display_currency_id = define.CURRENCY_ID['BASE_DSP_CURRENCY_ID']

        # dsp_currency_id 검사
        if self.cur.execute("SELECT `id`, `code` FROM `currency` WHERE `isdsp`=1 AND `id`=%(id)s;",
                            {'id': display_currency_id}):
            _, dsp_currency_code = self.cur.fetchone()
        else:
            return False, {}

        return True, {'id': display_currency_id, 'code': dsp_currency_code}


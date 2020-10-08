from lib.ApiView import ApiView
import time


class FeerateView(ApiView):
    """
    거래소의 출금, 거래 수수료와 회원 관련 수수료 데이터를 제공하는 API
    """
    DB_READONLY = True
    VERIFY_KEY = 'SECRETKEY'
    ALLOW_METHOD = "GET"

    def run(self):
        data = {
            'trade_commission': self.get_trade_commission,
            'withdraw_commission': self.get_withdraw_commission,
            'user': self.get_userfeegrade(self.secret_key.member_id) if self.secret_key.is_verify else None,
        }

        self.con.commit()
        self.Response(status='NORMAL', code='NORMAL', data=data)

    def get_userfeegrade(self, member_id):
        """
        회원의 수수료 등급과 각종 수수료들을 제공하는 메소드
        """
        user_fee_grades = dict()
        if member_id is not None:
            sql = "SELECT `tfr`, `mfr`, `update_date`, `tradeamount` FROM `mem_feerate_relation` WHERE `member_id`=%(member_id)s;"
            kwargs = {'member_id': member_id}
            if self.cur.execute(sql, kwargs):
                tfr, mfr, update_date, tradeamount = self.cur.fetchone()

                # feegrade 가져오기
                sql = "SELECT `grade` FROM `mem_feerate` WHERE `tradeamount` <= %(tradeamount)s AND `enable`=1 ORDER BY `grade` DESC LIMIT 1;"
                kwargs = {'tradeamount': tradeamount}
                self.cur.execute(sql, kwargs)
                feegrade = self.cur.fetchone()[0]
            else:
                feegrade = 1
                sql = "SELECT `tfr`, `mfr`, `tradeamount` FROM `mem_feerate` WHERE `grade`=%(grade)s;"
                kwargs = {'grade': feegrade}
                self.cur.execute(sql, kwargs)
                tfr, mfr, tradeamount = self.cur.fetchone()
                update_date = int(time.time())

            user_fee_grades['taker_feerate'] = str(tfr / 10 ** 4)
            user_fee_grades['maker_feerate'] = str(mfr / 10 ** 4)
            user_fee_grades['update_date'] = update_date
            user_fee_grades['trade_size'] = str(tradeamount / 10 ** 8)
            user_fee_grades['feerate_grade'] = str(feegrade)

            return user_fee_grades
        else:
            return None

    @property
    def get_trade_commission(self):
        """
        거래 수수료를 제공해주는 메소드
        """
        sql = "SELECT `grade`, `tfr`, `mfr`, `tradeamount` FROM `mem_feerate` WHERE `enable`=1 ORDER BY `grade` ASC;"

        trade_commission_list = list()
        if self.cur.execute(sql):
            for grade, tfr, mfr, tradeamount in self.cur.fetchall():
                trade_commissions = dict()
                trade_commissions['grade'] = grade
                trade_commissions['taker_feerate'] = str(tfr / 10 ** 4)
                trade_commissions['maker_feerate'] = str(mfr / 10 ** 4)
                trade_commissions['trade_size'] = str(tradeamount / 10 ** 8)

                trade_commission_list.append(trade_commissions)

        return trade_commission_list

    @property
    def get_withdraw_commission(self):
        """
        출금 수수료를 제공해주는 데이터
        """
        sql = "SELECT " \
              "`id`, `name_english`,`code`,`digit`, " \
              "`min_withdraw_amount`, " \
              "`withdraw_fee_type`, " \
              "`withdraw_fee_amount`, " \
              "`withdraw_fee_rate` " \
              "FROM `currency` ORDER BY `id` ASC;"

        withdraw_commission_list = list()
        if self.cur.execute(sql):
            for id, name_english, code, digit, min_withdraw_amount, withdraw_fee_type, withdraw_fee_amount, withdraw_fee_rate in self.cur.fetchall():
                withdraw_commissions = dict()
                withdraw_commissions['english_name'] = name_english
                withdraw_commissions['currency_code'] = code
                withdraw_commissions['min_withdraw_size'] = str(min_withdraw_amount / 10 ** digit)

                if withdraw_fee_type == 0:
                    withdraw_commissions['withdraw_fee_size'] = str(withdraw_fee_amount / 10 ** digit)
                elif withdraw_fee_type == 1:
                    withdraw_commissions['withdraw_fee_rate'] = str(withdraw_fee_rate / 10 ** 4)
                else:
                    withdraw_commissions['withdraw_fee_size'] = None

                withdraw_commission_list.append(withdraw_commissions)

        return withdraw_commission_list

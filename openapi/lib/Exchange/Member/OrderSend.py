# -*- encoding:utf8 -*-
from __future__ import unicode_literals

import json
from contextlib import contextmanager

import redis
from django.conf import settings


class OrderSend(object):
    def __init__(self, cursor, member):
        self.cur = cursor
        self.member = member

        self.rcon = None

    @contextmanager
    def established(self):
        try:
            self.rcon = redis.Redis(**settings.PUBLISH_DB)
            yield self
        finally:
            try:
                self.rcon.connection_pool.disconnect()
                self.rcon = None
            except Exception:
                pass

    def __call__(self, product_code, order_type,
                 policy=None, side=None, price=None, size=None, expire_seconds=None, magicnumber=None,
                 funds=None, order_id=None, cancel_size=None, stop_price=None,
                 ):
        assert order_type in ('MARKET', 'LIMIT', 'CANCEL', 'STOP', 'STOPCANCEL')
        assert side in (None, 'BUY', 'SELL')
        assert policy in (None, "GTC", "GTT")
        magicnumber = 0 if magicnumber is None else magicnumber

        ordrset = dict(
            member_id=self.member.member_id,
            wallet_id=self.member.wallet_id,
            broker_id='00000000-0000-0000-0000-000000000000',
            incomming='WEB',
            product=product_code,
            order_type=order_type,
        )
        if order_type == 'LIMIT':
            if policy == 'GTC':
                ordrset.update(dict(
                    policy=policy, side=side, price=price, size=size,
                    tfr=self.member.fee_rate['tfr'],
                    mfr=self.member.fee_rate['mfr'],
                    magicnumber=magicnumber,
                ))
            else:  # GTT
                ordrset.update(dict(
                    policy=policy, side=side, price=price, size=size,
                    tfr=self.member.fee_rate['tfr'],
                    mfr=self.member.fee_rate['mfr'],
                    magicnumber=magicnumber,
                    expire_seconds=expire_seconds,
                ))
        elif order_type == 'MARKET':
            if side == 'BUY':
                ordrset.update(dict(
                    side=side, funds=funds,
                    tfr=self.member.fee_rate['tfr'],
                    magicnumber=magicnumber,
                ))
            else:  # SELL
                ordrset.update(dict(
                    side=side, size=size,
                    tfr=self.member.fee_rate['tfr'],
                    magicnumber=magicnumber,
                ))
        elif order_type == 'CANCEL':
            if cancel_size is None:
                ordrset.update(dict(
                    order_id=order_id,
                ))
            else:
                ordrset.update(dict(
                    order_id=order_id,
                    size=cancel_size,
                ))
        elif order_type == 'STOP':
            if price is not None:  # Limit
                ordrset.update(dict(
                    stop_price=stop_price,
                    price=price,
                    amount=size,
                    side=side,
                    tfr=self.member.fee_rate['tfr'],
                    mfr=self.member.fee_rate['mfr'],
                    magicnumber=magicnumber,
                ))
            else:  # Market
                if side == 'BUY':
                    ordrset.update(dict(
                        stop_price=stop_price,
                        amount=funds,
                        side=side,
                        tfr=self.member.fee_rate['tfr'],
                        magicnumber=magicnumber,
                    ))
                else:  # SELL
                    ordrset.update(dict(
                        stop_price=stop_price,
                        amount=size,
                        side=side,
                        tfr=self.member.fee_rate['tfr'],
                        magicnumber=magicnumber,
                    ))
        elif order_type == 'STOPCANCEL':
            ordrset.update(dict(
                order_id=order_id,
            ))
        else:
            raise ValueError('UNKNOWN')
        if self.rcon is not None:
            self.rcon.lpush('ORDERSEND', json.dumps(ordrset))
        return ordrset

    def limit_gtc(self, product_code, side, price, size, magicnumber):
        with self.established():
            return self.__call__(
                order_type='LIMIT',
                policy='GTC',
                product_code=product_code,
                side=side,
                price=price,
                size=size,
                magicnumber=magicnumber,
            )

    def limit_gtt(self, product_code, side, price, size, magicnumber, expire_seconds):
        with self.established():
            return self.__call__(
                order_type='LIMIT',
                policy='GTT',
                product_code=product_code,
                side=side,
                price=price,
                size=size,
                magicnumber=magicnumber,
                expire_seconds=expire_seconds,
            )

    def market_buy(self, product_code, funds, magicnumber):
        with self.established():
            return self.__call__(
                order_type='MARKET',
                side="BUY",
                product_code=product_code,
                funds=funds,
                magicnumber=magicnumber,
            )

    def market_sell(self, product_code, size, magicnumber):
        with self.established():
            return self.__call__(
                order_type='MARKET',
                side="SELL",
                product_code=product_code,
                size=size,
                magicnumber=magicnumber,
            )

    def cancel(self, product_code, order_id, cancel_size=None):
        with self.established():
            return self.__call__(
                order_type='CANCEL',
                product_code=product_code,
                order_id=order_id,
                cancel_size=cancel_size,
            )

    def stop_limit(self, product_code, side, stop_price, price, size, magicnumber):
        with self.established():
            return self.__call__(
                order_type='STOP',
                product_code=product_code,
                side=side,
                stop_price=stop_price,
                price=price,
                size=size,
                magicnumber=magicnumber,
            )

    def stop_market_buy(self, product_code, stop_price, funds, magicnumber):
        with self.established():
            return self.__call__(
                order_type='STOP',
                product_code=product_code,
                side="BUY",
                stop_price=stop_price,
                funds=funds,
                magicnumber=magicnumber,
            )

    def stop_market_sell(self, product_code, stop_price, size, magicnumber):
        with self.established():
            return self.__call__(
                order_type='STOP',
                product_code=product_code,
                side="SELL",
                stop_price=stop_price,
                size=size,
                magicnumber=magicnumber,
            )

    def stopcancel(self, product_code, order_id):
        with self.established():
            return self.__call__(
                order_type='STOPCANCEL',
                product_code=product_code,
                order_id=order_id,
            )

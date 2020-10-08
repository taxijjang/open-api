from lib.ApiView import ApiView
import operator
import redis
import time
from django.conf import settings


class ProductCurrencyCode(ApiView):
    VERIFY_KEY = "APIKEY"
    ALLOW_METHOD = "GET"

    def run(self):
        product_codes, currency_codes = self.product_currency_code
        data = dict(
            product_code=product_codes,
            currency_code=currency_codes,
        )

        self.con.commit()
        return self.Response(data=data)

    @property
    def product_currency_code(self):
        """
        현재 상장되어 있는 상품리스트와 base_currency_code를 반환
        :return: 상장 되어 있는 상품 코드 리스트와 base_currency_code 반환
        """
        sql = "SELECT `product_name`, `base_currency_code` FROM `products` WHERE `product_status` = 2"
        self.cur.execute(sql)

        product_codes = list()
        currency_codes = list()
        for product_code, currency_code in self.cur.fetchall():
            product_codes.append(product_code)
            currency_codes.append(currency_code)

        return product_codes, currency_codes

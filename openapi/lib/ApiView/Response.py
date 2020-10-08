import json

from django.conf import settings
from django.shortcuts import HttpResponse


class Response:
    RESPONSE_STATUS = {
        'NORMAL': 200,
        'BAD_REQUEST': 400,
        'UNAUTHORIZED': 401,
        'FORBIDDEN': 403,
        'NOT_FOUND': 404,  # Server
        'TOO_MANY_REQUEST': 429,
        'INTERNAL_SERVER_ERROR': 500,  # Server
    }

    RESPONSE_CODES_NORAML = {
        'NORMAL': 0,  # 정상
        'NOT_FOUND': 404,  # 찾을수 없음

        # 10xxx // 사용자 관련
        'NOT_EXISTS_PRODUCT_CODE': 10010,  # 잘못된 product_id를 입력했음
        'NOT_ALLOW_PRODUCT_ORDER_TYPE': 10011,  # product가 금지되었습니다.
        'NOT_EXISTS_CURRENCY_ID': 10012,  # currency_id가 존재 하지 않는다.
        'NOT_EXISTS_DSP_CURRENCY_ID': 10013,  # dsp_currency_id 가 존재 하지 않는다.
        'NOT_ENOUGH_BALANCE': 10014,  # balance가 부족하다.
        'NOT_EXISTS_COUNTRY_ID': 10019,  # country_id가 존재하지 않는다.
        'NOT_EXISTS_UNIT': 10020,  # 존재 하지 않는 candle 단위
        'NOT_EXISTS_SIDE': 10021,  # 존재 하지 않는 매도/매수 타입
        'NOT_EXISTS_ORDER_TYPE': 10022,  # 존재 하지 않는 주문 타입

        # 111xx // ordersend 관련
        'NOT_EXISTS_ORDER_ID': 11100,  # 존재하지 않는 order_id
        'INVALID_TRADE_SIZE': 11101,  # 유효하지 않는 거래 사이즈
        'INVALID_MIN_TRADE_FUNDS': 11102,  # 최소 거래 대금을 초과함
        'INVALID_TRADE_PRICE': 11103,  # 유효하지 않는 가격
    }
    RESPONSE_CODES_BAD_REQUEST = {
        'REQUIRED_ARGUMENT': 20000,  # 필수입력 argument를 입력하지 않았음
        'INVALID_ARGUMENT': 20001,  # 잘못된 형식의 argument를 입력했음
        'INVALID_TYPE_ARGUMENT': 20002,
    }
    RESPONSE_CODES_UNAUTHORIZED = {
        'INVALID_APIKEY': 30000,  # apikey 인증 실패(key가 이상함)
        'SIGNATURE_APIKEY': 30001,  # apikey 인증 실패(key가 다름)

        'INVALID_SECRETKEY': 30100,  # secretkey 인증 실패(key가 이상함)
        'SIGNATURE_SECRETKEY': 30101,  # secretkey 인증 실패(key가 다름)

        'INVALID_AUTH_TOKEN': 30200,  # auth_token 인증 실패(token이 이상함)
        'SIGNATURE_AUTH_TOKEN': 30201,  # auth_token 인증 실패(secret_key가 다름)
        'EXPIRED_AUTH_TOKEN': 30202,  # auth_token 만료
        'TERMINATE_AUTH_TOKEN': 30203,  # auth_token 에 대한 secret_key가 삭제됨

        #### API KEY , SECRET KEY 에 대한 응답코드 만들어야됨 ####

        #####################################################
    }
    RESPONSE_CODES_FORBIDDEN = {
        'NOT_ALLOW_TRADE': 40012,  # 거래가 허용되지 않음
    }
    RESPONSE_CODES_THROTTLING = {
        'TOO_MANY_REQUEST': 50000,  # 시간 내 많은 request 호출 함 (현재 1분에 100회)
    }

    RESPONSE_CODES_INTERNAL_SERVER_ERROR = {
        # 90xxx 예상치 못한 상황
        'UNKNOWN': 90000,  # 예외처리 하지 못한 error에 대한 일괄처리
        'NOT_FOUND_MEMBER_ID': 90001,  # member테이블에 member_id가 존재 하지 않는다.
    }

    RESPONSE_CODES = dict()
    RESPONSE_CODES.update(RESPONSE_CODES_NORAML)
    RESPONSE_CODES.update(RESPONSE_CODES_BAD_REQUEST)
    RESPONSE_CODES.update(RESPONSE_CODES_UNAUTHORIZED)
    RESPONSE_CODES.update(RESPONSE_CODES_FORBIDDEN)
    RESPONSE_CODES.update(RESPONSE_CODES_INTERNAL_SERVER_ERROR)
    RESPONSE_CODES.update(RESPONSE_CODES_THROTTLING)

    def Response(self, status='NORMAL', code='NORMAL', data=None):
        '''
        :param status: 상태
        :param code: 코드
        :param data: 데이터
        :return: django.shortcuts.HttpResponse
        '''
        content = dict()
        content['status'] = self.RESPONSE_STATUS[status]
        content['code'] = self.RESPONSE_CODES[code]
        if data:
            content['data'] = data
        if settings.DEBUG:
            content['description'] = code
        self.HttpResponse = HttpResponse(content=json.dumps(content),
                                         content_type='application/json',
                                         status=content['status'],
                                         )

        self.HttpResponse["Server"] = "TWS"
        self.HttpResponse["Api-Version"] = 2.2  # 임시적인 해결책
        # self.HttpResponse["Expires"] = "3600"
        # self.HttpResponse["Cache-Control"] = 'public, max-age=3600'
        return self.HttpResponse

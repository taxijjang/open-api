# 메이져 거래소 OPEN API 제공 데이터

[고팍스](https://gopax.github.io/API/?lang=ko#6796537949)

[빗썸](https://apidocs.bithumb.com/docs/api_info)

[업비트](https://docs.upbit.com/reference)



## 공통 제공 Public 데이터

- 가상자산 거래 체결 완료 내역

- 가상자산 현재가 정보(Ticker)

- 가상자산 현재가 정보(Orderbook)

- 가상 자산의 입/출금 현황 정보

- 시간 및 구간 별 거래소 가상자산 가격, 거래량 정보


## 공통 제공 Private 데이터

- 회원의 및 코인 거래 수수료 정보

- 회원의 보유한 자산 리스트

- 회원의 코인 입금 지갑 주소

- 회원의 가상자산 거래 정보

- 회원의 매수/매도 등록 대기 또는 거래 중 내역 정보

- 회원의 매수/매도 체결 내역 상세 정보

- 회원의 거래 완료 내역 정보

- 주문 가능 정보

- 지정가 매수/매도 등록 기능

- 시장가 매수/매도 등록 기능

- 코인 입/출금

- 원화 입/출금


## 업비트 제공 API

- 마켓 코드 조회

- 분/일/주/월 단위 시세

## 고팍스 제공 API

- 거래쌍 목록 조회하기(GOPAX 거래소에서 취급하는 모든 거래쌍의 목록을 조회)

- 서버시간 조회

## 빗썸 제공 API

- 빗썸 지수 (BTMI,BTAI) 정보


## 거래소별 open API Data

 빈칸  | 인증방식|public api (요청 제한)| private api (요청 제한) | web socket 제공|
---|---|:---:|---|---
|  |   |--- 국내 ---    ||
|upbit|access key, secret key로 토큰 생성(jwt)|1초 10회<br> 분당 600회 | 주문 )1초 8회, 1분 200회 <br> 주문 외) 초당 30회, 분당 900회| O|
|bithumb|apikey, secret key|1초 135회 | 1초 135회 | O |
|gopax|apikey, signature, timestamp|1초 20회| 1초 20회 | X|
|korbit|OAuth2.0 으로 access token 발급|1초 12회| 1초 12회 | O|
|  |   |--- 해외 ---    ||
|binance|apikey, secret key|1초 6회| 1초 6회| O |
|poloniex|apikey, secret key|1초 6회| 1초 6회| O |
|bitfinex|apikey, signature|end point마다 다름|end point마다 다름 | O|




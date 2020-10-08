# 제공할 데이터


- 목차
    1. [체결내역](open_api_data.md#체결내역)
    1. [Ticker](open_api_data.md#Ticker)
    1. [order book](open_api_data.md#order-book)
    1. [시간 및 구간 별 거래소 가상자산 가격, 거래량 정보](open_api_data.md#시간-및-구간-별-거래소-가상자산-가격-거래량-정보)
    1. [상품코드 및 가상자산코드](open_api_data.md#상품코드-및-가상자산코드)
    1. [수수료 정보](open_api_data.md#수수료-정보)
    1. [내 자산](open_api_data.md#내-자산)
    1. [지정가 매수/매도](open_api_data.md#지정가-매수매도)
    1. [시장가 매수/매도](open_api_data.md#시장가-매수매도)
    1. [예약가 매수/매도](open_api_data.md#예약가-매수매도)
    1. [지정가 매수/매도 취소](open_api_data.md#지정가-매수매도-취소)
    1. [예약가 매수/매도 취소](open_api_data.md#예약가-매수매도-취소)
    1. [주문 내역](open_api_data.md#주문내역)
    1. [거래 내역](open_api_data.md#거래내역)


---

# Public

### 체결내역
```GET``` /v1/tradehistory

##### Request Parameters

요청변수| 설명 | 타입
-- | -- | --
product_code | 상품영문코드 (EX) ETHKRW ) | String
tradehistory_count | 체결내역 갯수 | int(default = 10)

##### Response

필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String
price | 가격 | string
amount | 수량 | string
timestamp | 체결시각 | int
product_code | 상품영문코드 (EX) ETHKRW ) | String
side | BUY/SELL/All |String


---

### Ticker
```GET``` /v1/ticker

##### Request Parmas

요청변수| 설명 | 타입
-- | -- | --
product_code| 상품영문코드 (EX) ETHKRW ) | String

##### Response


필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
side | BUY/SELL |String
min_price_unit | 최소 가격 단위 | string
min_amount_unit | 최소 수량 단위 | string
trade_funds_24h | 24시간 거래량 | string
trade_price | 최종 체결가 | string
product_code| 상품영문코드 (EX) ETHKRW ) | String



---
### order book
```GET``` /v1/orderbook

##### Request Parmas
요청변수| 설명 | 타입
-- | -- | --
product_code| 상품영문코드 (EX) ETHKRW ) | String
count | 갯수 (1 ~ 30) 기본값 : 30 | int

##### Response
필드 | 설명| 타입
-----|------|---------
status|상태코드|string
timestamp | 타임스탬프 |integer
product_code| 상품영문코드 (EX) ETHKRW ) | String
bid| 매수정보| map
ask| 매도정보| map
min_amount_unit | 최소 수량 단위 | string
min_price_unit | 최소 가격 단위 | string

##### bid, ask(map)
필드 | 설명| 타입
-----|------|---------
key | 수량 | string
value | 가격 | string


---


### 시간 및 구간 별 거래소 가상자산 가격, 거래량 정보

##### 분(minute)
```GET``` /v1/candles/minutes

##### Request Parmas
요청변수 | 설명 | 타입
-----------|------|-------
unit | 단위(1분, 5분, 15분, 30분) | integer
product_code| 상품영문코드 (EX) ETHKRW ) | String
count | 갯수(default=10, limit=1~30) | int

##### 시(hour)
```GET``` /v1/candles/hour

##### Request Parmas
요청변수 | 설명 | 타입
-----------|------|-------
unit | 단위(1시간, 4시간) | integer
product_code| 상품영문코드 (EX) ETHKRW ) | String
count | 갯수(default=10, limit=1~30) | int

##### 일(day)
```GET``` /v1/candles/days

##### Request Parmas
요청변수 | 설명 | 타입
-----------|------|-------
unit | 단위(1일) | integer
product_code| 상품영문코드 (EX) ETHKRW ) | String
count | 갯수(default=10, limit=1~30) | int

##### 주(week)

```GET``` /v1/candles/weeks

##### Request Parmas
요청변수 | 설명 | 타입
-----------|------|-------
unit | 단위(1주) | integer
product_code| 상품영문코드 (EX) ETHKRW ) | String
count | 갯수(default=10, limit=1~30) | int




##### Response
필드 | 설명 | 타입
------|------|------
open|시가 | string
high|고가 | string
low | 저가 | string
close | 종가 | string
volumn | 거래량 | string
timestamp | 타임스탬프 | int


---

### 상품코드 및 가상자산코드
```GET``` /v1/ currency/code


##### Request Parameters

요청 변수 | 설명 | 타입
 --       |  --  | ---

##### Response

필드 | 설명 | 타입
 -- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String
currency_code_list | 가상자산 code 목록 (EX) ETH | List
product_code_list | 상품영문코드 목록 (EX) ETHKRW ) | List


##### currency_list

필드 | 설명 | 타입
 -- | -- | --
currency_code | 가상자산 code (EX) ETH ) | String

##### product_code_list

필드 | 설명 | 타입
 -- | -- | --
product_code | 상품영문코드 (EX) ETHKRW ) | String

---
# Private


### 수수료 정보
```GET``` /v1/feerate

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수



##### Request Parameters

요청 변수 | 설명 | 타입
-- | -- | --




##### Response

필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String
withdraw_commission | 출금 수수료 | List
trade_commission | 거래 수수료 | List
user | 유저 수수료 및 거래 대금 합계 | Map


---


### 내 자산
```GET``` /v1/assets

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수

##### Request Parameters

요청 변수 | 설명 | 타입
-- | -- | --
currency_code_list| 가상자산 영문코드 (EX) ETH | List

##### Response

필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String
assets | 보유한 자산들 | Map

##### Assets (map)

필드 | 설명 | 타입
-- | -- | --
balance | 보유량 | string
accum_withdraw |  출금 총합 | string
accum_deposit | 입금 총합 | string
hold | 미체결수량 | string
avg_price| 평균매수가 | string
currency_code | 해당 자산 영문코드 | String




---

### 지정가 매수/매도
```POST``` /order/limit

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수

##### Request Parameters

요청 변수 | 설명 | 타입
-- | -- | --
product_code | 상품영문코드 (EX) ETHKRW ) | String
price | 지정가 | String
side | BUY/SELL |String
amount | 수량 | String
magicnumber| 주문 구분 번호 | int

##### Response


필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String

---

### 시장가 매수/매도
```POST``` /order/market


##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수

##### Request Parameters

요청 변수 | 설명 | 타입
-- | -- | --
product_code | 상품영문코드 (EX) ETHKRW ) | String
side | BUY/SELL |String
amount | 수량 | String
magicnumber| 주문 구분 번호 | int

##### Response


필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String


---

### 예약가 매수/매도
```POST``` /order/stop

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수

##### Request Parameters

요청 변수 | 설명 | 타입
-- | -- | --
product_code | 상품영문코드 (EX) ETHKRW ) | String
stop_price | 예약주문가 | string
price | 지정가 | string
side | BUY/SELL |String
amount | 수량 | string
magicnumber| 주문 구분 번호 | int

##### Response


필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String

---


### 지정가 매수/매도 취소
```DELETE``` /v1/order/cancel

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수

##### Request Params
요청 변수 | 설명 | 타입
-- | -- | --
order_id | 주문 번호 | string/필수

##### Response

필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String




---

### 예약가 매수/매도 취소
```DELETE``` /v1/order/stopcancel

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수

##### Request Params

요청 변수 | 설명 | 타입
-- | -- | --
order_id | 주문 번호 | string


##### Response

필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String

---

### 주문내역

```GET``` /v1/orderhistory

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수

##### Request Params

요청 변수 | 설명 | 타입
-- | -- | --
order_id | 주문 번호 | string


##### Response

필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String
stop_price | 예약가 | String
order_type |  MARKET/LIMIT/STOP  | String
price | 체결가 | String
base_currency_code | 주문통화 | String
quote_currency_code | 결제통화 | String
amount | 주문 수량 | String
timestamp | 주문 시각 | Int
side | BUY/SELL/All |String
magicnumber| 주문 구분 번호 | int


### 거래내역
```GET``` /v1/transactionhistory

##### Request header
요청 헤더 | 설명 | 타입
-- | -- | --
apiKey | 사용자 API Key | String/필수
secretKey | 사용자 Secret Key | String/필수


##### Request Parameters

요청 변수 | 설명 | 타입
-- | -- | --
order_type |  MARKET/LIMIT/STOP  | String
product_code_list | 상품영문코드 (EX) ETHKRW ) | List
side | BUY/SELL/All |String

##### Response

필드 | 설명 | 타입
-- | -- | --
status | 결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조) | String
order_list | 주문 목록 | list

- order_list (map)

필드 | 설명 | 타입
-- | -- | --
product_code | 상품영문코드 (EX) ETHKRW ) | List
order_type |  MARKET/LIMIT/STOP  | String
order_id | 주문 id | string
done_time | 체결 시각 | int
fee | 수수료 | string
quote_currency_code | 결제통화 | String
amount | 체결 수량 | string
price |  거래 가격 | string
total_price | 총 체결액 | string
base currency code | 주문 통화 | String
side | BUY/SELL/All |String
magicnumber| 주문 구분 번호 | int






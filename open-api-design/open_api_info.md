# API 정보

---


## API 설계


### 1. 리소스 소비자


- 거래소를 이용하는 고객


### 2. 인증 방식

- [인증방식](https://github.com/LandWhale2/open-api-design/blob/master/open_api_auth.md)


### 3.  문서 관리


- md나 등등을 이용하여 직접 작성 (비 효율적)


- API 문서 자동화툴을 이용 하여 작성 (drf-yasg, swagger 등등) 


---

## Public


### 1. 체결내역

- DB table: tradehistory
- file: Order/__init__.py
- class name: order_history_list

---

### 2. Ticker
필드|설명
------|-------
status|상태 코드
timestamp|타임 스탬프
trade_price|최종 체결가
high|고가 24시 이전
low|저가 24시 이전
open|시가 24시 이전
close|종가 24시 이전
volume|24시간 거래량
change|24시간 이전 가격과 현재가격 차이
changePercent|24시간 이전 가격과 현재가격 차이 비율

- DB table: product, OHLC:{qcd/bcd}:{time}

- file: CCE-pbws/WebSocket.py

- class name: PBWSNamespace

---

### 3. Order Book

- DB table: order:OPEN

- file: CCE-pbws/Publisher.py/OrderbookThread
        CCE-pbws/Message.py/Response/Orderbook
---

### 4. 시간 및 구간 별 거래소 가상자산 가격, 거래량 정보

<추가 예정>

---

## Private

### 1.수수료 정보

- DB table: mem_feerate
- file: views_info.py
- class name: commision

---

### 3. 자산

- DB table: <각 코인 대문자 이름>:order:HISTORY:<balanch, detail, hold,summary>
- file: views.assets.py
- class name: assets_list_get

---

### 4. 매수, 매도

#### A. 지정가 매수/매도, B. 시장가 매수/매도

  - 지정가 -> order_type: 1 ,  시장가 -> order_type: 0
  - DB table: order:OPEN
  - file: Order/...
  
#### C. 예약가 매수/매도

  - DB table: order:STOP
  - file: Order/Stop.py, StopCancle.py

#### D. 매수/매도 취소


---

### 5. 거래 내역

#### A. 주문내역

- DB table: <각 코인 대문자 이름>:order:HISTORY
- file: Order/__init__.py
- class name: order_history_list

#### B. 거래내역

- DB table: <개인 memeber_id>:order:DONE
- file: Order/__init__.py
- class name: order_done_list

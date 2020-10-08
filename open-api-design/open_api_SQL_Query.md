# oepn API SQL Query

### 체결내역
##### SQL Query
사용자는 실시간 체결내역의 데이터를 얻고자 한다. 그러므로 web socket에서 제공해주는 data를 넘겨주어야 한다.
 
 ```
 > - SELECT `price`/100000000 AS `price`, `size`/100000000 AS `size` , `done_time`/100000000 AS `timestamp`, `product`AS `product_code`, `side` AS `side` FROM `order:DONE` WHERE `product` = "{PRODUCT_CODE}" ORDER BY `done_time` DESC  LIMIT 10
 ```


### order book
사용자는 실시간 order book의 데이터를 얻고자 한다. 그러므로 web socket에서 제공해주는 data를 넘겨주어야 한다.

```
##### SQL Query
 > - ask(낮은가격정렬)
 > - SELECT `price`/100000000 AS `ask` FROM `order:OPEN` WHERE `product` = '{PRODUCT_CODE}'  ORDER BY `price` ASC LIMIT {COUNT}
```
 
 
 > - bid(높은가격정렬)
 > - SELECT `price`/100000000 AS `bid` FROM `order:OPEN` WHERE `product` = '{PRODUCT_CODE}'  ORDER BY `price` DESC LIMIT {COUNT}

### 상품코드 및 가상자산코드
##### SQL Query
 > - SELECT `product_name`, `base_currency_code`, `product_status` FROM `products`


### 시장가 매수/ 매도
##### 매수/ 매도
- Market.py
```
self.member.OrderSend.market_buy(
    product_code=self.product['code'],
    funds=self.InputArgument['amount'],
    magicnumber=self.InputArgument['magicnumber'],
)
```
```  
self.member.OrderSend.market_sell(
    product_code=self.product['code'],
    size=amount,
    magicnumber=self.InputArgument['magicnumber'],
)
```  
- OrderSend.py  
```
ordrset = dict(
    member_id=self.member.member_id,
    wallet_id=self.member.wallet_id,
    broker_id='00000000-0000-0000-0000-000000000000',
    incomming='WEB',
    product=product_code,
    order_type=order_type,
)
```

```
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
```

- redis 
```
 if self.rcon is not None:
 self.rcon.lpush('ORDERSEND', json.dumps(ordrset))
```


### 시장가 취소
##### 취소
- Cancel.py
```
self.member.OrderSend.cancel(
            product_code=self.cancelorder['product_code'],
            order_id=self.InputArgument['order_id'],
            cancel_size=cancel_size,
        )
```
- OrderSend.py  
```
ordrset = dict(
    member_id=self.member.member_id,
    wallet_id=self.member.wallet_id,
    broker_id='00000000-0000-0000-0000-000000000000',
    incomming='WEB',
    product=product_code,
    order_type=order_type,
)
```
```
def cancel(self, product_code, order_id, cancel_size=None):
    with self.established():
        return self.__call__(
            order_type='CANCEL',
            product_code=product_code,
            order_id=order_id,
            cancel_size=cancel_size,
        )
```
- redis 
```
 if self.rcon is not None:
 self.rcon.lpush('ORDERSEND', json.dumps(ordrset))
```

### 주문내역

##### SQL Query
 
 - ```order_id```가 예약주문으로 대기 중인지 확인(예약주문이 완료되었다면 여기서 나오지 않음)
 
 > - SELECT `stop_price`,`price`,`bcc`,`qcc`,`size`/100000000 AS `size`,`time`, `side` FROM `order:STOP` WHERE `order_id` = "e7bc8d28-fc07-4db8-8d3c-b9b93775ee43"
 
 - ```order_id```가 예약주문이 아니라면 {PRODUCT_CODE}를 찾아서 {PRODUCT_CODE}에 해당하는 History테이블을 참조 해야함 (해당 {PRODUCT_CODE}를 찾는 query)
 
 > - SELECT `product` FROM `order:DONE` WHERE `order_id` = "e3c869c5-3994-4d4a-8957-d3a258dd160b" 
UNION SELECT `product` FROM `order:OPEN` WHERE `order_id` = "e3c869c5-3994-4d4a-8957-d3a258dd160b" 

- ```{PRODUCT_CODE}```를 찾고 해당 {PRODUCT_CODE}에 해당되는 테이블에서 order_id를 찾음 (history_type가 1이면 예약주문, history_type가 0이면 예약주문 X)

> - SELECT `stop_price`, `history_type`, `order_type`, `price`/100000000 AS `price`, `bcc`, `qcc`, `amount`/100000000, `time`, `side`  FROM `HBCKRW:order:HISTORY`
WHERE `order_id`="d298230b-4e10-40ad-b4a3-6a02313f2582" ORDER BY `identity`  

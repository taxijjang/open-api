# 인증 방식


# API Key, Secret Key 이용

## 사용자의 Key 발급 조건

### 1. 특정 인증 레벨 이상 사용자만 가능

### 2. 거래 금지 또는 계정 금지 사용자 X

---

## apikey, secretkey 
Authorization 헤더 방식을 이용하여
apikey, secretkey HTTP의 header로 전송


---

### API Key, Secret Key 테이블 생성

- 테이블 값 : key, mem_id, 생성시간, 호출횟수(호출제한 위해서)

---

# API, Secret Key 암호화 방식

## API Key (Authentication), Secret Key (Authorization)
- 각각의 키는 회원당 1개의 키를 가지도록 한다.
- public api에 접근시 api key를 이용, private api에 접근시 api key, secret key 둘다 이용
- 키를 발급 받을때 두개의 키 (api, secret)를 동시에 제공해준다.
- secret key는 보안을 위해 발급 후 일정시간만 보여주도록 한다.
- 무분별한 키의 생성을 막기 위해 발급 후 일정시간이 지나야 재발급이 가능하도록 한다.


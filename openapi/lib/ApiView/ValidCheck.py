import json
import re
import socket
import copy
import datetime


class ValidCheck:
    def InputValidCheck(self):
        """InputArgumentValidSet을 입력 받아서 validcheck를 실행함"""
        try:
            self.request.META['CONTENT_TYPE']
        except KeyError:
            self.request.META['CONTENT_TYPE'] = 'application/json'
        if self.request.body:
            try:
                request_body = json.loads(self.request.body)
            except ValueError:
                self.Response(status='BAD_REQUEST', code='INVALID_ARGUMENT')
                return False
        elif self.request.GET:
            body = self.request.GET
            try:
                json_body = json.dumps(body)
                request_body = json.loads(json_body)
            except ValueError:
                self.Response(status='BAD_REQUEST', code='INVALID_ARGUMENT')
                return False
        else:
            request_body = {}

        for validset in self.InputArgumentValidSet:
            if validset['require']:  # 필수
                try:
                    _value = request_body[validset['key']]
                except KeyError:
                    self.Response(status='BAD_REQUEST', code='REQUIRED_ARGUMENT', data={'key': validset['key']})
                    return False
                except TypeError:
                    self.Response(status='BAD_REQUEST', code='INVALID_TYPE_ARGUMENT', data={'key': validset['key']})
                    return False
            else:
                try:
                    _value = request_body[validset['key']]
                except KeyError:
                    _value = validset['defaultvalue']

            # None 확인
            if validset['require']:  # 필수
                if _value == None:  # 필수값에 None이 들어오면 INVALID_ARGUMENT
                    self.Response(status='BAD_REQUEST', code='INVALID_ARGUMENT', data={'key': validset['key']})
                    return False
            else:  # 옵션
                if validset[
                    'defaultvalue'] != None and _value == None:  # defaultvalue가 None을 허용, default가 None이 아니면 None 허용하지 않음
                    self.Response(status='BAD_REQUEST', code='INVALID_ARGUMENT', data={'key': validset['key']})
                    return False

            # datatype
            try:
                if _value == None:
                    value = _value
                elif validset['kind'] == 'unit':
                    value = validset['datatype'](_value)
                elif validset['kind'] == 'array':
                    value = list()
                    for v in _value:
                        value.append(validset['datatype'](v))

                else:
                    raise ValueError('UNKNOWN')

            except Exception as err:
                self.Response(status='BAD_REQUEST', code='INVALID_ARGUMENT', data={'key': validset['key']})
                return False

            # casting
            _value = copy.deepcopy(value)
            if _value == None:
                value = _value
            elif validset['kind'] == 'unit':
                value = self.__castings(castings=validset['castings'], value=value)
            elif validset['kind'] == 'array':
                value = list()
                for _v in _value:
                    v = self.__castings(castrings=validset['castings'], value=_v)
                    value.append(v)
            else:
                raise ValueError('UNKNOWN')

            # validcheck
            if value == None:
                pass
            elif validset['kind'] == 'unit':
                if not self.__validtype(validset=validset, value=value):
                    self.Response(status='BAD_REQUEST', code='INVALID_ARGUMENT', data={'key': validset['key']})
                    return False
            elif validset['kind'] == 'array':
                for v in value:
                    if not self.__validtype(validset=validset, value=v):
                        self.Response(status='VAD_REQUEST', code='INVALID_ARGUMENT', data={'key': validset['key']})
                        return False

            else:
                raise ValueError('UNKNOWN')

            self.InputArgument[validset['key']] = value

        return True

    def __castings(self, castings, value):
        for cast in castings:
            if cast == 'upper':
                return str(value).upper()
            elif cast == 'lower':
                return str(value).lower()
            elif cast == 'strip':
                return str(value).strip()
            else:
                raise ValueError('UNKNOWN')
        else:
            return value

    def __validtype(self, validset, value):
        validtypes = validset['validtypes']
        for validtype in validtypes:
            if validtype == 'boolean':
                r = self.__validchk_boolean(value=value)
            elif validtype == 'zero':
                r = self.__validchk_zero(number=value)
            elif validtype == 'nonzero':
                r = self.__validchk_nonzero(number=value)
            elif validtype == 'timestamp10':
                r = self.__validchk_timestamp(timestamp=value, num=10)
            elif validtype == 'timestamp13':
                r = self.__validchk_timestamp(timestamp=value, num=13)
            elif validtype == 'timestamp16':
                r = self.__validchk_timestamp(timestamp=value, num=16)
            elif validtype == 'uuid':
                r = self.__validchk_uuid(_uuid=value)
            elif validtype == 'email':
                r = self.__validchk_email(email=value)
            elif validtype == 'ip':
                r = self.__validchk_ip(ip=value)
            elif validtype == 'enum':
                r = self.__validchk_enum(value=value, enumSet=validset['enum'])
            elif validtype == 'length':  # datatype only str
                r = self.__validchk_length(value=value, lengthSet=validset['length'])
            elif validtype == 'range':
                r = self.__validchk_range(value=value, rangeSet=validset['range'])
            elif validtype == 'date':
                r = self.__validchk_date(value=value)
            elif validtype == 'isnum':
                r = self.__validchk_isnum(value=value)
            elif validtype == 'currency':
                r = self.__validchk_currency(value=value)
            elif validtype == 'product':
                r = self.__validchk_product(value=value)
            elif validtype == 'float_nonzero':
                r = self.__validchk_nonzero_float(number=value)
            else:
                raise ValueError('UNKNOWN')

            if not r:
                return False

        return True

    def __validchk_currency(self, value):
        SRE_Match = re.match('^[A-Z]{1}[A-Z0-9]{0,5}$', value)
        if SRE_Match is not None:
            return True
        else:
            return False

    def __validchk_product(self, value):
        SRE_Match = re.match('^[A-Z]{1}[A-Z0-9]{0,11}$', value)
        if SRE_Match is not None:
            return True
        else:
            return False

    def __validchk_isnum(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def __validchk_date(self, value):
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def __validchk_range(self, value, rangeSet):
        if rangeSet['min'] and value < rangeSet['min']:
            return False
        if rangeSet['max'] and value > rangeSet['max']:
            return False
        return True

    def __validchk_length(self, value, lengthSet):
        if lengthSet['min'] and len(value) < lengthSet['min']:
            return False
        if lengthSet['max'] and len(value) > lengthSet['max']:
            return False
        return True

    def __validchk_enum(self, value, enumSet):
        if value in enumSet:
            return True
        else:
            return False

    def __validchk_boolean(self, value):
        if int(value) in (0, 1):
            return True
        else:
            return False

    def __validchk_zero(self, number):
        if int(number) >= 0:
            return True
        else:
            return False

    def __validchk_nonzero(self, number):
        if int(number) > 0:
            return True
        else:
            return False

    def __validchk_timestamp(self, timestamp, num):
        try:
            datetime.datetime.fromtimestamp(int(timestamp) / 10 ** (num - 10))
            return True
        except ValueError:
            return False

    def __validchk_uuid(self, _uuid):
        if re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', str(_uuid)):
            return True
        else:
            return False

    def __validchk_email(self, email):
        if re.match('^[_a-zA-Z0-9-+]+(\.[_a-zA-Z0-9-+]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$',
                    str(email)):
            return True
        else:
            return False

    def __validchk_ip(self, ip):
        try:
            n = int(socket.inet_aton(str(ip)).encode('hex'), 16)
            if 0 <= n <= 4294967295:
                return True
            else:
                return False
        except socket.error:
            return False

    def __validchk_nonzero_float(self, number):
        if not float(number) == 0:
            return True
        else:
            return False
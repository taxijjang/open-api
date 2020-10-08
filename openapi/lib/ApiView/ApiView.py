import time
import json
import traceback
import logging

from django.db import connections, IntegrityError, ProgrammingError, OperationalError, DataError
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.conf import settings
from lib import DB
from lib import Exchange

from ..libTools import cached_property
from .Headers import Headers
from .ValidCheck import ValidCheck
from .Response import Response
from . import Key


class ApiView(View, Response, ValidCheck):
    #########
    # SETUP #
    #########
    context = None
    current_time = None
    args = None
    kwargs = None
    request = None
    headers = None
    con = None
    cur = None
    api_key = None
    secret_key = None

    ALLOW_METHOD = ["GET", "POST"]
    DB_READONLY = False

    VERIFY_KEY = "APIKEY"  # APIKEY | SECRETKEY
    VERIFY_KEY_FORCE = True

    FUNC_CHECK_TRADE = False

    InputArgumentValidSet = list()

    def setup(self, *args, **kwargs):
        self.current_time = time.time()

        self.args = args
        self.kwargs = kwargs

        self.request = self.args[0]
        self.headers = Headers(self.request)

        self.setup_database()
        self.setup_keys()

    def setup_database(self):
        if self.DB_READONLY:
            self.con = DB.StorageDB(connections['readonly'])
        else:
            self.con = DB.StorageDB(connections['default'])
        self.cur = self.con.cursor()
        self.db_IntegrityError = IntegrityError
        self.db_ProgrammingError = ProgrammingError
        self.db_OperationalError = OperationalError
        self.db_DataError = DataError

    def setup_keys(self):
        self.api_key = Key.Key.ApiKey(cursor=self.cur, api_key=self.headers.API_KEY)
        self.secret_key = Key.Key.SecretKey(cursor=self.cur, api_key=self.headers.API_KEY, secret_key=self.headers.SECRET_KEY)

    def verify_key_process(self):
        if self.VERIFY_KEY is None:
            return None
        elif self.VERIFY_KEY == 'APIKEY':
            try:
                self.api_key.verify()
                return None
            except Key.exceptions.InvalidKeyError:
                return self.Response(status='UNAUTHORIZED', code='INVALID_APIKEY')
            except Key.exceptions.NotVerifyKeyError:
                return self.Response(status='UNAUTHORIZED', code='INVALID_APIKEY')
        elif self.VERIFY_KEY == 'SECRETKEY':
            try:
                self.secret_key.verify()
                return None
            except Key.exceptions.InvalidKeyError:
                return self.Response(status='UNAUTHORIZED', code='INVALID_SECRETKEY')
            except Key.exceptions.NotVerifyKeyError:
                return self.Response(status='UNAUTHORIZED', code='INVALID_SECRETKEY')
        else:
            raise ValueError('UNKNOWN')

    def memstatus_function_check(self):
        if self.secret_key.is_verify:
            func_check_sets = [
                # (ischeck, flag, response_code),
                (self.FUNC_CHECK_TRADE, self.secret_key.trade, 'NOT_ALLOW_TRADE'),
            ]
            for ischeck, flag, response_code in func_check_sets:
                if ischeck and flag == 0:
                    return self.Response(status='FORBIDDEN', code=response_code)
        return None

    ###########
    # Running #
    ###########
    def previous_run(self):
        return None

    def run(self):
        pass

    def before_argument_parsing(self):
        pass

    def __call__(self, *args, **kwargs):
        if args[0].method.upper() not in self.ALLOW_METHOD:
            return HttpResponse(status=405)

        response = self.verify_key_process()

        if self.VERIFY_KEY_FORCE and response is not None:
            self.con.rollback()
            return response

        response = self.memstatus_function_check()
        if response is not None:
            self.con.rollback()
            return response

        if self.request.method.upper() == "POST":
            self.before_argument_parsing()
            self.InputArgument = dict()
            if self.InputArgumentValidSet:
                if not self.InputValidCheck():
                    self.con.rollback()
                    return self.HttpResponse
            # Running
            response = self.previous_run()
            if response is not None:
                return response
            self.run()
            return self.HttpResponse
        elif self.request.method.upper() == "GET":
            self.before_argument_parsing()
            self.InputArgument = dict()
            if self.InputArgumentValidSet:
                if not self.InputValidCheck():
                    self.con.rollback()
                    return self.HttpResponse
            response = self.previous_run()
            if response is not None:
                return response
            self.run()
            return self.HttpResponse
        else:
            raise ValueError("UNKNOWN")

    def exception_wrapper(self, *args, **kwargs):
        self.setup(*args, **kwargs)
        try:
            response = self.__call__(*args, **kwargs)
            if self.con._execute_count > 0:
                self.con.rollback()
            return response
        except Exchange.exceptions.NotFoundMemberIdError as err:
            data = {'member_id': err.member_id}
            response = self.Response(status='INTERNAL_SERVER_ERROR', code="NOT_FOUND_MEMBER_ID", data=data)
        except Http404 as err:
            raise Http404(err)
        except Exception as err:
            logging.critical(traceback.format_exc(err))
            data = {'traceback': traceback.format_exc(err)}
            response = self.Response(status='INTERNAL_SERVER_ERROR', code='UNKNOWN', data=data)
        try:
            self.con.rollback()
        except Exception:
            pass
        return response

    def post(self, *args, **kwargs):
        return self.exception_wrapper(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.exception_wrapper(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return HttpResponse(status=405)

    def options(self, *args, **kwargs):
        self.setup(*args, **kwargs)
        if settings.DEBUG:
            data = {
                'key': {
                    'kind': self.VERIFY_KEY,
                    'force': self.VERIFY_KEY_FORCE,
                },
            }
            if self.InputArgumentValidSet:
                arguments = dict()
                for each in self.InputArgumentValidSet:
                    item = dict()
                    item['require'] = each['require']
                    item['datatype'] = each['datatype'].__name__
                    item['kind'] = each['kind']
                    if not each['require']:
                        item['defaultvalue'] = each['defaultvalue']

                    item['validtypes'] = list()
                    for validtype in each['validtypes']:
                        if validtype == 'length':
                            item['validtypes'].append({validtype: each['length']})
                        elif validtype == 'enum':
                            item['validtypes'].append({validtype: each['enum']})
                        elif validtype == 'range':
                            item['validtypes'].append({validtype: each['range']})
                        else:
                            item['validtypes'].append({validtype: True})

                    item['castings'] = list()
                    for casting in each['castings']:
                        item['castings'].append(casting)

                    arguments[each['key']] = item
                data['arguments'] = arguments
            response = HttpResponse(json.dumps(data, indent=4, sort_keys=True), content_type='application/json')
        else:
            response = HttpResponse()
        response['Allow'] = self.ALLOW_METHOD
        return response

    def head(self, *args, **kwargs):
        return HttpResponse(status=405)

    ############################
    # Api View Global Property #
    ############################

    @cached_property
    def member_id(self):
        if self.secret_key.is_verify:
            return self.secret_key.member_id
        else:
            return None

    @cached_property
    def member(self):
        print(self.member_id)
        return Exchange.Member(self.cur, self.member_id)

    @cached_property
    def txsetting(self):
        pass

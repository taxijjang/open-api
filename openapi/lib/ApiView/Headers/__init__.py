import re

from ...libTools import cached_property


class HeadersDescriptor:
    def __init__(self, name):
        self.name = name

    def __set__(self, instance, value):
        error = "'{class_name}' object attribute '{name}' is read-only".format(
            class_name=instance.__class__.__name__,
            name=self.name,
        )
        raise AttributeError(error)

    def __get__(self, instance, owner):
        return instance.headers.get(self.name, None)

class Headers:
    API_KEY = HeadersDescriptor('API_KEY')
    SECRET_KEY = HeadersDescriptor('SECRET_KEY')

    def __init__(self, request):
        self.request = request

    @cached_property
    def headers(self):
        headers = dict()
        for envkey in self.request.environ.keys():
            if re.match('^HTTP_.+$', envkey):
                headers[envkey[5:]] = self.request.environ[envkey]
        return headers

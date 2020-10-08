from django.core.cache import cache as cache
from lib.ApiView.Response import Response


class ThrottlingMiddleware(Response, object):
    """

    API 호출 제한을 하기 위한 Custom middleware

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.META['HTTP_API_KEY'])
        user_api_key = request.META['HTTP_API_KEY']

        cache.get_or_set(key=user_api_key, default=0, timeout=60)

        request_count = cache.incr(key=user_api_key, delta=1)

        print(request_count)
        if request_count > 500:
            return self.process_request(request)
        else:
            return self.get_response(request)

    def process_request(self, request):
        return self.Response(status='TOO_MANY_REQUEST', code='TOO_MANY_REQUEST')

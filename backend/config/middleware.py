from django.conf import settings


class IPAndHeaderCheckMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME']))
        print(request.COOKIES.get("Authorization"))

        response = self.get_response(request)
        return response

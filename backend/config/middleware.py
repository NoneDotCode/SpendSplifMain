from django.http import JsonResponse


class CheckHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        print(host)

        response = self.get_response(request)
        return response

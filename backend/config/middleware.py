from django.http import JsonResponse


class IPAndHeaderCheckMiddleware:
    ALLOWED_IPS = ('34.38.192.230', '127.0.0.1', '172.18.0.1')
    EXPO_APP_KEY = 'd142c3a6-34df-4c3e-993e-fa14fa88d94f'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        if ip not in self.ALLOWED_IPS:
            expo_app_key = request.headers.get('EXPO-APP-KEY')
            if expo_app_key != self.EXPO_APP_KEY:
                print(ip)
                print(expo_app_key)
                return JsonResponse({'detail': 'Forbidden: Invalid EXPO-APP-KEY or IP address'}, status=403)

        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

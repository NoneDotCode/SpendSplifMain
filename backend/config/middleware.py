from django.http import JsonResponse


class CheckExpoAppIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_app_id = 'd142c3a6-34df-4c3e-993e-fa14fa88d94f'

    def __call__(self, request):
        expo_app_id = request.headers.get('Expo-App-ID')
        if expo_app_id != self.allowed_app_id:
            return JsonResponse({'error': 'Forbidden'}, status=403)

        response = self.get_response(request)
        return response

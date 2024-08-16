from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import re


class UserAgentMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        user_agent = request.headers.get('User-Agent', '')
        expo_app_key = request.META.get('HTTP_EXPO_APP_KEY', '')
        print("key:" + expo_app_key)

        browser_user_agents = [
            'Mozilla',
            'Chrome',
            'Safari',
            'Firefox',
            'Edge',
            'Opera'
        ]

        if 'okhttp' in user_agent:
            if expo_app_key == 'd142c3a6-34df-4c3e-993e-fa14fa88d94f':
                print("OK")
                return None

            print("FAIL")
            print(request.headers)
            return JsonResponse({'error': 'Forbidden'}, status=403)

        if any(re.search(agent, user_agent) for agent in browser_user_agents):
            return None

        return JsonResponse({'error': 'Forbidden'}, status=403)

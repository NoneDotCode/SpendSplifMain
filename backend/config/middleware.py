from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import re


class UserAgentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        expo_app_key = request.META.get('HTTP_EXPO_APP_KEY', '')

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
            else:
                print("FAIL")
                print(request.META)
                return JsonResponse({'error': 'Forbidden'}, status=403)

        if any(re.search(agent, user_agent) for agent in browser_user_agents):
            return None

        return JsonResponse({'error': 'Forbidden'}, status=403)

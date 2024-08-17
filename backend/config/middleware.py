from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import re
from django.conf import settings


class UserAgentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_agent = request.headers.get('User-Agent', '')
        expo_app_key = request.headers.get('EXPO-APP-KEY', '')

        browser_user_agents = [
            'Mozilla',
            'Chrome',
            'Safari',
            'Firefox',
            'Edge',
            'Opera',
        ]

        if "Stripe" in user_agent:
            return self.get_response(request)

        if 'okhttp' in user_agent:
            if expo_app_key == settings.EXPO_APP_KEY:
                return self.get_response(request)

            return JsonResponse({'error': 'Forbidden'}, status=403)

        if any(re.search(agent, user_agent) for agent in browser_user_agents):
            return self.get_response(request)

        return JsonResponse({'error': 'Forbidden'}, status=403)

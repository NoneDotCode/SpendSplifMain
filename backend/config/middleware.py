from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import re


class UserAgentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        secure_key = request.META.get('APP_SECURE_KEY', '')

        browser_user_agents = [
            'Mozilla',
            'Chrome',
            'Safari',
            'Firefox',
            'Edge',
            'Opera'
        ]

        if 'okhttp' in user_agent:
            if secure_key == '60o3rRQfk*A{Ccnwc~%krywuvJp6lcJwvLw@~{DC6R2C#dRHOr':
                return None
            else:
                return JsonResponse({'error': 'Forbidden'}, status=403)

        if any(re.search(agent, user_agent) for agent in browser_user_agents):
            return None

        return JsonResponse({'error': 'Forbidden'}, status=403)

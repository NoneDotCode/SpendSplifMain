from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import re
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from backend.apps.space.models import Space


class UserAgentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_agent = request.headers.get('User-Agent', '')
        secure_key = request.headers.get('APP_SECURE_KEY', '')

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


class UpdateSpaceLastModifiedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ["POST", "PUT"]:
            # Регулярное выражение для URL с API-версией и идентификатором спейса
            match = re.match(r"^/api/v1/my_spaces/(?P<space_pk>\d+)/", request.path)
            if match:
                space_id = match.group("space_pk")
                # Обновление last_modified для Space
                space = get_object_or_404(Space, id=space_id)
                space.last_modified = now()
                space.save()

        response = self.get_response(request)
        return response
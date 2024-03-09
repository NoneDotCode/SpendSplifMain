from backend.apps.space.models import Space
from backend.apps.space.models import MemberPermissions

from django.contrib import admin

admin.site.register(Space)
admin.site.register(MemberPermissions)

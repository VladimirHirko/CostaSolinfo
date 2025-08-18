# backend/core/throttling.py
from rest_framework.throttling import SimpleRateThrottle

class ContactFormThrottle(SimpleRateThrottle):
    scope = 'contact_form'

    def get_cache_key(self, request, view):
        # по IP; можно заменить на user.id, если нужна привязка к пользователю
        ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}

from rest_framework.throttling import AnonRateThrottle
from mathtest.settings import DEFAULT_REQUEST_RATE_LIMIT


class CustomAnonThrottle(AnonRateThrottle):
    def get_rate(self):
        return DEFAULT_REQUEST_RATE_LIMIT

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None  # Only throttle unauthenticated requests.
        view_name = view.__class__.__name__ if view else ''
        return self.cache_format % {
            'scope': f'{self.scope}{view_name}',
            'ident': self.get_ident(request)
        }

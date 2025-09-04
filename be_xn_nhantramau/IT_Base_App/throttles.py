from rest_framework.throttling import UserRateThrottle, BaseThrottle
from rest_framework.settings import api_settings


class HighRateThrottle(UserRateThrottle):
    scope = 'high'


class LowRateThrottle(UserRateThrottle):
    scope = 'low'
    request = None

    def allow_request(self, request, view):
        """
        Check if the request should be throttled.
        """
        # Get the authenticated user (if any)
        user = request.user
        self.request = request
        print(user)

        return super().allow_request(request, view)

    def wait(self):
        """
                This method is called when the request is throttled.
                """
        # Get the IP address from the request
        ip_address = self.get_ident(self.request)
        print(ip_address)

        # Return the recommended wait time (e.g., using DRF default settings)
        return


class MediumRateThrottle(UserRateThrottle):
    scope = 'medium'


class OverHighRateThrottle(UserRateThrottle):
    scope = 'over_high'

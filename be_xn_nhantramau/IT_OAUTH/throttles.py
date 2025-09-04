# =========================================================================
# File: app/throttles.py
# Description: Optimized DRF throttle classes with IP banning logic.
# =========================================================================
import json
from IT_OAUTH.models import IPManager
from IT_OAUTH.serializers import serialize_request
from datetime import datetime, timedelta
from rest_framework.throttling import UserRateThrottle
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.Logging.logging_tools import LogHelperOnlyString

# Logger for throttling-related issues
logger_bug_string_throttle = LogHelperOnlyString("log_throttle_bug")

# =========================================================================
# IPBanMixin: A mixin for adding IP-based banning to any throttle class.
# This mixin encapsulates the core logic to prevent code duplication.
# =========================================================================


class IPBanMixin:
    """
    A mixin that checks for banned IP addresses and handles the
    response if a request is from a banned IP.
    """
    request = None  # To hold the request object for the wait() method

    def check_for_banned_ip(self, request):
        """
        Helper method to check if the current IP is in the IPManager table.
        Returns the IPManager object if found, otherwise None.
        """
        try:
            datetime_current = datetime.now()
            return IPManager.objects.using("default").filter(
                ip=self.get_ident(request),
                time_expired__gt=datetime_current,
                active=True,
            ).first()
        except Exception as e:
            logger_bug_string_throttle.warning(
                "500",
                "IPBanMixin::check_for_banned_ip Error",
                f"Failed to check IPManager: {e}"
            )
            return None

    def allow_request(self, request, view):
        """
        Overrides the base method to first check for a banned IP.
        """
        self.request = request
        ip_manager = self.check_for_banned_ip(request)

        # If an IPManager entry exists, the IP is banned.
        # Returning None or a falsy value from allow_request
        # causes the DRF framework to call the wait() method.
        if ip_manager:
            return False

        # If not banned, continue with the standard rate limiting check.
        # The parent class's allow_request handles this logic.
        return super().allow_request(request, view)

    def wait(self):
        """
        Overrides the base method. This is called when allow_request returns False.
        This method either returns the remaining ban time or creates a new ban.
        """
        ip_address = self.get_ident(self.request)
        path = self.request.build_absolute_uri()

        try:
            datetime_current = datetime.now()
            # Re-check for the IPManager record, in case it was created by a
            # different concurrent request (though unlikely in this flow).
            ip_manager = self.check_for_banned_ip(self.request)

            if ip_manager:
                # IP is already banned, return the remaining time.
                total_seconds_remain = (
                    ip_manager.time_expired - datetime_current).total_seconds()
                return total_seconds_remain
            else:
                # If we get here, it means the request was throttled by the
                # parent class's logic, not by an existing ban.
                # We should now create a new ban for this IP.

                # Set ban duration to 2 days (midnight of the 2nd day).
                new_datetime = (datetime_current + timedelta(days=2)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

                ip_manager = IPManager()
                ip_manager.user = self.request.user if self.request.user else None
                ip_manager.ip = ip_address
                ip_manager.path = path
                ip_manager.request = serialize_request(self.request)
                ip_manager.error_name = ip_manager.ERROR_SPAM
                ip_manager.time_expired = new_datetime

                # Using database_sync_to_async is not necessary here because DRF's
                # throttle methods are executed in a synchronous context.
                ip_manager.save()

                # A new ban was created, so return the duration of the ban.
                return (new_datetime - datetime_current).total_seconds()

        except Exception as e:
            logger_bug_string_throttle.warning(
                "500",
                "IPBanMixin::wait Error",
                f"Failed to save IPManager ban entry for IP {ip_address}: {e}"
            )
            # Fallback to the default wait time from the parent class
            return super().wait()


# =========================================================================
# Optimized Throttle Classes inheriting from the new mixin.
# =========================================================================

class HighRateThrottle(IPBanMixin, UserRateThrottle):
    scope = "high"


class LowRateThrottle(IPBanMixin, UserRateThrottle):
    scope = "low"
    # This class uses the standard DRF rate limiting and does not
    # require the custom IP banning logic.


class MediumRateThrottle(UserRateThrottle):
    scope = "medium"


class OverHighRateThrottle(UserRateThrottle):
    scope = "over_high"


class SuperRateThrottle(IPBanMixin, UserRateThrottle):
    scope = "super"

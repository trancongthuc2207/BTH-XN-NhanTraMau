from rest_framework.throttling import UserRateThrottle, BaseThrottle
from rest_framework.settings import api_settings
import json
from .models import IPManager
from datetime import datetime, timedelta
from .serializers import serialize_request


class HighRateThrottle(UserRateThrottle):
    scope = "high"
    request = None

    def allow_request(self, request, view):
        """
        Check if the request should be throttled.
        """
        # Get the authenticated user (if any)
        user = request.user
        self.request = request
        try:
            # print("--- CHECK Throttles Running")
            datetime_current = datetime.now()
            ip_manager = (
                IPManager.objects.using("default")
                .filter(
                    ip=self.get_ident(request),
                    time_expired__gt=datetime_current,
                    active=True,
                )
                .first()
            )
            # return to wait()
            if ip_manager:
                return
            # print("--- PASSED CHECK Throttles")
        except Exception as e:
            print("--- CHECK Throttles Fails")

        return super().allow_request(request, view)

    def wait(self):
        """
        This method is called when the request is throttled.
        """
        # Get the IP address from the request
        ip_address = self.get_ident(self.request)
        path = self.request.build_absolute_uri()
        try:
            datetime_current = datetime.now()
            # ---- check is banned ---- #
            ip_manager = (
                IPManager.objects.using("default")
                .filter(
                    ip=ip_address,
                    time_expired__gt=datetime_current,
                    active=True,
                )
                .first()
            )
            if ip_manager:
                totals_sencond_remain = (
                    ip_manager.time_expired - datetime_current
                ).total_seconds()
                return totals_sencond_remain
            # -------------------------- #

            # Add 2 days
            new_datetime = datetime_current + timedelta(days=2)
            # Set time to 00:00:00
            new_datetime = new_datetime.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            ip_manager = IPManager()
            ip_manager.user = (
                None if not self.request.user else self.request.user
            )
            ip_manager.ip = ip_address
            ip_manager.path = path
            ip_manager.request = serialize_request(self.request)
            ip_manager.error_name = ip_manager.ERROR_SPAM
            ip_manager.time_expired = new_datetime
            ip_manager.save()
        except Exception as e:
            print("--- Fail for save Throttles")

        # Return the recommended wait time (e.g., using DRF default settings)
        return


class LowRateThrottle(UserRateThrottle):
    scope = "low"
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
    scope = "medium"


class OverHighRateThrottle(UserRateThrottle):
    scope = "over_high"


class SuperRateThrottle(UserRateThrottle):
    scope = "super"
    request = None

    def allow_request(self, request, view):
        """
        Check if the request should be throttled.
        """
        # Get the authenticated user (if any)
        user = request.user
        self.request = request
        try:
            # print("--- CHECK Throttles Running")
            datetime_current = datetime.now()
            ip_manager = (
                IPManager.objects.using("default")
                .filter(
                    ip=self.get_ident(request),
                    time_expired__gt=datetime_current,
                    active=True,
                )
                .first()
            )
            # return to wait()
            if ip_manager:
                return
            # print("--- PASSED CHECK Throttles")
        except Exception as e:
            print("--- CHECK Throttles Fails")

        return super().allow_request(request, view)

    def wait(self):
        """
        This method is called when the request is throttled.
        """
        # Get the IP address from the request
        ip_address = self.get_ident(self.request)
        path = self.request.build_absolute_uri()
        try:
            datetime_current = datetime.now()
            # ---- check is banned ---- #
            ip_manager = (
                IPManager.objects.using("default")
                .filter(
                    ip=ip_address,
                    time_expired__gt=datetime_current,
                    active=True,
                )
                .first()
            )
            if ip_manager:
                totals_sencond_remain = (
                    ip_manager.time_expired - datetime_current
                ).total_seconds()
                return totals_sencond_remain
            # -------------------------- #

            # Add 2 days
            new_datetime = datetime_current + timedelta(days=2)
            # Set time to 00:00:00
            new_datetime = new_datetime.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            ip_manager = IPManager()
            ip_manager.user = (
                None if not self.request.user else self.request.user
            )
            ip_manager.ip = ip_address
            ip_manager.path = path
            ip_manager.request = serialize_request(self.request)
            ip_manager.error_name = ip_manager.ERROR_SPAM
            ip_manager.time_expired = new_datetime
            ip_manager.save()
        except Exception as e:
            print("--- Fail for save Throttles")

        # Return the recommended wait time (e.g., using DRF default settings)
        return

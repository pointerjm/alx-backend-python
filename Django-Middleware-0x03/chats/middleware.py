import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict
import time as time_module

# Configure a logger for requests
logger = logging.getLogger("request_logger")


# 1. Logging User Requests (Basic Middleware)
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        response = self.get_response(request)
        return response


# 2. Restrict Chat Access by Time
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allowed window: 6 AM to 9 PM (06:00 - 21:00)
        now = datetime.now().time()
        if not (time(6, 0) <= now <= time(21, 0)):
            return HttpResponseForbidden("Chat is only accessible between 6AM and 9PM.")

        return self.get_response(request)


# 3. Detect and Block Offensive Language (Rate Limiting by IP)
class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_by_ip = defaultdict(list)  # Track timestamps of requests per IP

    def __call__(self, request):
        if request.method == "POST" and "/messages" in request.path:
            ip = self.get_client_ip(request)
            now = time_module.time()

            # Remove old requests outside the 1-minute window
            self.requests_by_ip[ip] = [
                ts for ts in self.requests_by_ip[ip] if now - ts < 60
            ]

            if len(self.requests_by_ip[ip]) >= 5:
                return HttpResponseForbidden("Rate limit exceeded: Max 5 messages per minute.")

            # Track this request
            self.requests_by_ip[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


# 4. Enforce Chat User Role Permissions
class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Restrict certain paths to admins/moderators only
        protected_paths = ["/admin", "/chats/moderate"]

        if any(request.path.startswith(p) for p in protected_paths):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required.")
            if not (request.user.is_superuser or getattr(request.user, "role", "") in ["admin", "moderator"]):
                return HttpResponseForbidden("You do not have permission to access this resource.")

        return self.get_response(request)

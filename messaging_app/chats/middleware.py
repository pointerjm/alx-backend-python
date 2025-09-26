import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden
from django.utils.timezone import now
from collections import defaultdict

# Configure logger for requests
logger = logging.getLogger("request_logger")
file_handler = logging.FileHandler("requests.log")
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """Logs each user request with timestamp, user and path."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """Restricts access to chats outside 6AM - 9PM."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = now().hour
        if request.path.startswith("/chats/"):  # restrict only chats
            if current_hour < 6 or current_hour >= 21:
                return HttpResponseForbidden("❌ Access restricted outside 6AM - 9PM")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Limits number of chat messages a user can send in 1 minute,
    based on IP address (max 5 messages).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.message_log = defaultdict(list)  # {ip: [timestamps]}

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/chats/messages/"):
            ip = self.get_client_ip(request)
            now_time = datetime.now()

            # Clean up old timestamps (older than 1 min)
            self.message_log[ip] = [
                ts for ts in self.message_log[ip] if now_time - ts < timedelta(minutes=1)
            ]

            if len(self.message_log[ip]) >= 5:
                return HttpResponseForbidden("🚫 Rate limit exceeded: Max 5 messages per minute")

            # Record new message timestamp
            self.message_log[ip].append(now_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Retrieve client IP address."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class RolePermissionMiddleware:
    """
    Restrict access to certain actions based on user role.
    Only admins and moderators can proceed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/chats/admin/"):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("❌ Authentication required")

            if not request.user.is_staff and not request.user.is_superuser:
                return HttpResponseForbidden("❌ Access denied: insufficient permissions")

        return self.get_response(request)

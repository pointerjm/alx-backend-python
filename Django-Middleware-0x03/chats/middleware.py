import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, JsonResponse

# Setup logger for requests
logger = logging.getLogger(__name__)
handler = logging.FileHandler("requests.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """Logs every request with timestamp, user, and path"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_entry)
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """Restricts chat access between 9PM and 6PM"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if current_hour >= 21 or current_hour < 6:
            return HttpResponseForbidden("Chat access restricted during off-hours (9PM - 6PM).")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """Rate limits chat messages per IP (5 per minute)"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}  # {ip: [timestamps]}

    def __call__(self, request):
        if request.method == "POST" and "/chats/" in request.path:
            ip = self.get_client_ip(request)
            now = datetime.now()

            if ip not in self.requests:
                self.requests[ip] = []

            # Keep only timestamps within the last 1 minute
            self.requests[ip] = [t for t in self.requests[ip] if now - t < timedelta(minutes=1)]

            if len(self.requests[ip]) >= 5:
                return JsonResponse({"error": "Rate limit exceeded. Max 5 messages per minute."}, status=429)

            self.requests[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR", "")


class RolePermissionMiddleware:
    """Restricts certain actions to admin or moderator roles"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = ["/admin/", "/moderate/"]

        if any(request.path.startswith(p) for p in protected_paths):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required.")
            if not (request.user.is_superuser or getattr(request.user, "role", "") in ["admin", "moderator"]):
                return HttpResponseForbidden("You do not have permission to access this resource.")

        return self.get_response(request)

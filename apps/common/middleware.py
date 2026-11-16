import json
import logging
import time
import uuid

logger = logging.getLogger("apps.http")


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.request_id = request_id

        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        response["X-Request-ID"] = request_id

        user_id = getattr(request.user, "id", None) if hasattr(request, "user") else None
        log_payload = {
            "event": "http.request",
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "user_id": str(user_id) if user_id else None,
        }
        logger.info(json.dumps(log_payload))

        return response
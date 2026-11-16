from django.db import connection
from django.http import JsonResponse


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        db_status = "ok"
    except Exception:
        return JsonResponse({"status": "error", "database": "unreachable"}, status=503)

    return JsonResponse({"status": "ok", "database": db_status}, status=200)
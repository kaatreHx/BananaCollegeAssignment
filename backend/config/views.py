"""Service health probe used by the frontend and deployment checks."""

from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        database = "ok"
    except Exception:
        database = "unavailable"

    return JsonResponse(
        {
            "status": "ok" if database == "ok" else "degraded",
            "service": "banana-blitz-api",
            "version": "1.0.0",
            "database": database,
            "time": timezone.now().isoformat(),
        }
    )

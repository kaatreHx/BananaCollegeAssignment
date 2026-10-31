from django.contrib import admin
from django.urls import include, path

from config.views import health
from game.views import LeaderboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/auth/", include("accounts.urls")),
    path("api/game/", include("game.urls")),
    path("api/leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("api/events/", include("events.urls")),
]

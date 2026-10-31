from django.urls import path

from .views import (
    ActiveGameView,
    LeaderboardView,
    NextRoundView,
    StartGameView,
    SubmitAnswerView,
)

urlpatterns = [
    path("start/", StartGameView.as_view(), name="game-start"),
    path("active/", ActiveGameView.as_view(), name="game-active"),
    path("answer/", SubmitAnswerView.as_view(), name="game-answer"),
    path("next/", NextRoundView.as_view(), name="game-next"),
]

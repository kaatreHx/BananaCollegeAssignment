"""Game HTTP API: start, active, answer, next — plus the public leaderboard."""

from django.db.models import Max
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .banana import BananaServiceError
from .services import (
    GameError,
    active_session,
    leaderboard,
    next_round_for,
    round_payload,
    session_payload,
    start_game,
    submit_answer,
)
from .serializers import AnswerSerializer


class StartGameView(APIView):
    """POST /api/game/start/ → new run (GameSession + round 1)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            session, round_obj = start_game(request.user)
        except BananaServiceError:
            return Response(
                {"error": {"code": "puzzle_service_unavailable", "message": "The banana puzzle service is unavailable. Try again."}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {"session": session_payload(session), "round": round_payload(round_obj)},
            status=status.HTTP_201_CREATED,
        )


class ActiveGameView(APIView):
    """GET /api/game/active/ → the open puzzle, if a run is in progress."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = active_session(request.user)
        if not session:
            return Response({"session": None, "round": None})
        return Response(
            {"session": session_payload(session), "round": round_payload(session.current_round)}
        )


class SubmitAnswerView(APIView):
    """POST /api/game/answer/ {round_id, answer}. No session id in the URL."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = submit_answer(
                request.user,
                serializer.validated_data["round_id"],
                serializer.validated_data["answer"],
            )
        except GameError as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}}, status=exc.status
            )
        return Response(payload)


class NextRoundView(APIView):
    """POST /api/game/next/ → retry serving the next puzzle after a 503."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            round_obj = next_round_for(request.user)
        except BananaServiceError:
            return Response(
                {"error": {"code": "puzzle_service_unavailable", "message": "Still loading. Try again."}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except GameError as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}}, status=exc.status
            )
        return Response({"round": round_payload(round_obj)})


class LeaderboardView(APIView):
    """GET /api/leaderboard/ — public, no login required."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"entries": leaderboard()})

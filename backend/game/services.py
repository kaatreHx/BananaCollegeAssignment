"""Game rules, kept in one place and independent of the HTTP layer."""

import logging

from django.db import transaction
from django.utils import timezone

from accounts.models import Player
from events.broker import broadcast

from .banana import BananaServiceError, banana_client
from .models import GameSession, Round

logger = logging.getLogger("game")

TOTAL_ROUNDS = 10
POINTS_PER_CORRECT = 1


class GameError(Exception):
    def __init__(self, message: str, code: str = "game_error", status: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


def round_payload(round_obj: Round) -> dict:
    """Public projection of a puzzle. The `solution` field is never included."""
    return {
        "id": str(round_obj.pk),
        "index": round_obj.index,
        "image_url": round_obj.image_url,
        "served_at": round_obj.served_at.isoformat(),
    }


def session_payload(session: GameSession) -> dict:
    return {
        "id": str(session.pk),
        "score": session.score,
        "rounds_played": session.rounds_played,
        "total_rounds": TOTAL_ROUNDS,
        "played_at": session.played_at.isoformat(),
    }


def start_game(user: Player) -> tuple[GameSession, Round]:
    """Create a fresh run (one GameSession row) and serve round 1."""
    puzzle = banana_client.fetch_puzzle()  # fail before creating any state

    with transaction.atomic():
        GameSession.objects.filter(user=user, rounds_played__lt=TOTAL_ROUNDS).delete()
        session = GameSession.objects.create(user=user)
        round_obj = Round.objects.create(
            session=session, index=1, image_url=puzzle.image_url, solution=puzzle.solution
        )
        session.current_round = round_obj
        session.save(update_fields=["current_round"])

    logger.info("game started user=%s session=%s", user.email, session.pk)
    return session, round_obj


def active_session(user: Player) -> GameSession | None:
    """The user's unfinished run, if any (finishes at 10 rounds)."""
    return (
        GameSession.objects.filter(user=user, rounds_played__lt=TOTAL_ROUNDS)
        .select_related("current_round")
        .first()
    )


def submit_answer(user: Player, round_id: str, answer) -> dict:
    """Score one answer. Correct = +1. After 10 rounds the run is over."""
    now = timezone.now()

    with transaction.atomic():
        try:
            round_obj = Round.objects.select_for_update().select_related("session").get(pk=round_id)
        except (Round.DoesNotExist, ValueError, TypeError):
            raise GameError("That puzzle does not exist.", "invalid_round", 404)

        session = round_obj.session
        if session.user_id != user.pk:
            raise GameError("That puzzle belongs to another player.", "not_yours", 403)
        if session.current_round_id != round_obj.pk:
            raise GameError("This puzzle has already been answered.", "already_answered", 409)

        answer_is_valid = isinstance(answer, int) and not isinstance(answer, bool)
        # Scoring is simple: the matching number wins, whenever it arrives.
        correct = bool(answer_is_valid and answer == round_obj.solution)
        points = POINTS_PER_CORRECT if correct else 0

        round_obj.answered_at = now
        round_obj.player_answer = answer if answer_is_valid else None
        round_obj.is_correct = correct
        round_obj.save(update_fields=["answered_at", "player_answer", "is_correct"])

        session.score += points
        session.rounds_played += 1
        session.current_round = None
        session.save(update_fields=["score", "rounds_played", "current_round"])

    finished = session.rounds_played >= TOTAL_ROUNDS
    if finished:
        # Event-driven: every open leaderboard page gets pinged to refresh.
        transaction.on_commit(
            lambda: broadcast(
                "leaderboard.updated",
                {"name": user.name, "score": session.score, "top": leaderboard(limit=5)},
            )
        )
    next_round = None
    if not finished:
        try:
            next_round = _serve_next_round(session)
        except BananaServiceError:
            pass  # keeps progress; the client retries with /game/next/

    result = {
        "correct": correct,
        "correct_answer": round_obj.solution,
        "player_answer": round_obj.player_answer,
        "points": points,
    }
    return {
        "result": result,
        "session": session_payload(session),
        "next_round": round_payload(next_round) if next_round else None,
        "needs_next": next_round is None and not finished,
        "finished": {"score": session.score, "played_at": session.played_at.isoformat()}
        if finished
        else None,
    }


def _serve_next_round(session: GameSession) -> Round:
    """Fetch a fresh puzzle and attach it to this run."""
    puzzle = banana_client.fetch_puzzle()
    with transaction.atomic():
        locked = GameSession.objects.select_for_update().get(pk=session.pk)
        round_obj = Round.objects.create(
            session=locked, index=locked.rounds_played + 1,
            image_url=puzzle.image_url, solution=puzzle.solution,
        )
        locked.current_round = round_obj
        locked.save(update_fields=["current_round"])
    session.current_round = round_obj
    return round_obj


def next_round_for(user: Player) -> Round:
    """Retry point when the next puzzle failed to load (`needs_next`)."""
    session = active_session(user)
    if not session:
        raise GameError("No run in progress. Start a new run.", "no_open_round", 404)
    if session.current_round and not session.current_round.answered_at:
        return session.current_round  # there is already an open puzzle
    return _serve_next_round(session)


def leaderboard(limit: int = 50) -> list[dict]:
    """All-time best score per player, from completed runs."""
    from django.db.models import Max

    rows = (
        GameSession.objects.filter(rounds_played__gte=TOTAL_ROUNDS)
        .values("user_id")
        .annotate(best=Max("score"))
        .order_by("-best")[:limit]
    )
    players = Player.objects.in_bulk([row["user_id"] for row in rows])
    return [
        {
            "rank": position,
            "score": row["best"],
            "name": players[row["user_id"]].name if row["user_id"] in players else "Unknown",
        }
        for position, row in enumerate(rows, start=1)
    ]

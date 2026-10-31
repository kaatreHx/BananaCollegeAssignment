"""Game tables.

GameSession  — one run of the game: user, score, played_at.
Round        — one puzzle inside a run: image, server-side solution.
"""

import uuid

from django.db import models

from accounts.models import Player


class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="sessions")
    score = models.PositiveIntegerField(default=0)
    rounds_played = models.PositiveSmallIntegerField(default=0)
    current_round = models.ForeignKey(
        "Round", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-played_at"]

    def __str__(self):
        return f"{self.user.name} · {self.score} pts"


class Round(models.Model):
    """A single puzzle. `solution` never leaves the server before answering."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="rounds")
    index = models.PositiveSmallIntegerField()
    image_url = models.URLField(max_length=500)
    solution = models.PositiveSmallIntegerField()

    served_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    player_answer = models.SmallIntegerField(null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(fields=["session", "index"], name="unique_round_index"),
        ]

    def __str__(self):
        return f"Round {self.index} of {self.session_id}"

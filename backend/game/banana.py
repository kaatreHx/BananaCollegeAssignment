"""Client for the external banana puzzle API (interoperability boundary)."""

import logging
from dataclasses import dataclass

import requests
from django.conf import settings

logger = logging.getLogger("game")


class BananaServiceError(Exception):
    """Raised when the external puzzle service cannot provide a usable puzzle."""


@dataclass(frozen=True)
class BananaPuzzle:
    image_url: str
    solution: int


class BananaClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = base_url or settings.BANANA_API_URL
        self.timeout = timeout or settings.BANANA_API_TIMEOUT

    def fetch_puzzle(self) -> BananaPuzzle:
        """One HTTPS call, validated. Raises BananaServiceError when unusable."""
        response = requests.get(
            self.base_url,
            params={"out": "json"},
            timeout=self.timeout,
            headers={"Accept": "application/json", "User-Agent": "BananaBlitz/1.0"},
        )
        response.raise_for_status()
        return self._parse(response.json())

    @staticmethod
    def _parse(payload: dict) -> BananaPuzzle:
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object.")

        image_url = str(payload.get("question", "")).strip()
        solution = payload.get("solution")

        if not image_url.startswith(("http://", "https://")):
            raise ValueError("Puzzle image URL is missing or invalid.")
        if isinstance(solution, bool):
            raise ValueError("Puzzle solution is invalid.")
        try:
            solution_int = int(solution)
        except (TypeError, ValueError) as exc:
            raise ValueError("Puzzle solution is not a number.") from exc
        if not 0 <= solution_int <= 999:
            raise ValueError("Puzzle solution is out of range.")

        return BananaPuzzle(image_url=image_url, solution=solution_int)


banana_client = BananaClient()

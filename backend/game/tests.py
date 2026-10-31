from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Player

from game.banana import BananaServiceError

PUZZLE = {"question": "https://example.com/puzzle.png", "solution": 7}


def make_puzzle(solution=7):
    return {"question": f"https://example.com/{solution}.png", "solution": solution}


class GameTests(APITestCase):
    def setUp(self):
        self.player = Player.objects.create_user(
            email="player@example.com", name="Player", password="StrongBanana42!"
        )
        self.client.force_authenticate(self.player)

    def start(self):
        with mock.patch("game.services.banana_client") as client:
            client.fetch_puzzle.side_effect = lambda: type(
                "P", (), {"image_url": make_puzzle()["question"], "solution": make_puzzle()["solution"]}
            )()
            response = self.client.post(reverse("game-start"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def test_start_creates_session_and_round(self):
        data = self.start()
        self.assertEqual(data["session"]["score"], 0)
        self.assertEqual(data["round"]["index"], 1)
        self.assertNotIn("solution", data["round"])  # never leaks the answer

    def test_correct_answer_scores_one_point(self):
        data = self.start()
        with mock.patch("game.services.banana_client") as client:
            # Next-puzzle fetch fails → needs_next; scoring must still succeed.
            client.fetch_puzzle.side_effect = BananaServiceError("down")
            response = self.client.post(
                reverse("game-answer"),
                {"round_id": data["round"]["id"], "answer": 7},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.data
        self.assertTrue(body["result"]["correct"])
        self.assertEqual(body["session"]["score"], 1)
        self.assertTrue(body["needs_next"])

    def test_wrong_answer_scores_zero(self):
        data = self.start()
        with mock.patch("game.services.banana_client") as client:
            client.fetch_puzzle.side_effect = BananaServiceError("down")
            response = self.client.post(
                reverse("game-answer"), {"round_id": data["round"]["id"], "answer": 3}, format="json"
            )
        self.assertFalse(response.data["result"]["correct"])
        self.assertEqual(response.data["session"]["score"], 0)

    def test_ten_correct_answers_finish_the_run(self):
        for _ in range(10):
            data = self.start() if _ == 0 else None
            if _ == 0:
                round_id = data["round"]["id"]
            else:
                active = self.client.get(reverse("game-active")).data
                round_id = active["round"]["id"]
            with mock.patch("game.services.banana_client") as client:
                client.fetch_puzzle.side_effect = lambda: type(
                    "P", (), {"image_url": "https://x/1.png", "solution": 7}
                )()
                response = self.client.post(
                    reverse("game-answer"), {"round_id": round_id, "answer": 7}, format="json"
                )
        self.assertEqual(response.data["session"]["score"], 10)
        self.assertTrue(response.data["finished"])

    def test_leaderboard_ranks_best_completed_score(self):
        self.start()
        with mock.patch("game.services.banana_client") as client:
            client.fetch_puzzle.side_effect = lambda: type(
                "P", (), {"image_url": "https://x/1.png", "solution": 7}
            )()
            for _ in range(10):
                active = self.client.get(reverse("game-active")).data
                self.client.post(
                    reverse("game-answer"),
                    {"round_id": active["round"]["id"], "answer": 7},
                    format="json",
                )
        self.client.force_authenticate(None)
        response = self.client.get(reverse("leaderboard"))
        self.assertEqual(response.data["entries"], [
            {"rank": 1, "score": 10, "name": "Player"}
        ])

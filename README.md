# Banana Blitz 🍌

A small full-stack game for a college assignment. Log in, solve banana
puzzles (images served by the [UOB banana API](https://marcconrad.com/uob/banana/api.php)),
get **1 point per correct answer**, and appear on a public leaderboard.

- Frontend: React + TypeScript + Vite
- Backend: Django + PostgreSQL
- Realtime: Server-Sent Events (SSE)

## The two tables (that's the whole schema)

| Table | Columns |
| --- | --- |
| `Player` | name, email, password |
| `GameSession` | user, score, played_at |

Plus one gameplay table: `Round` (which puzzle, image url, the correct
answer — kept server-side so nobody can cheat).

## How to run

```bash
# Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # then put your Postgres settings in .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver

# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

Backend: `http://127.0.0.1:8000/api` · Frontend: `http://localhost:5173`

## How to use the app

1. Open `http://localhost:5173` and **Sign up** (name, email, password).
2. You land on **Play**. Click **Start run** — a puzzle image appears.
3. Type the number the banana is worth and press **Submit**.
   Correct = +1 point. 10 puzzles per run.
4. Open **Leaderboard** — anyone can view it without logging in, and it
   refreshes on its own when any run finishes.

## API (all under `/api`)

| Endpoint | Auth | What it does |
| --- | --- | --- |
| `POST /auth/register/` | public | Create a player, returns JWT tokens |
| `POST /auth/login/` | public | Log in by email + password |
| `GET /auth/me/` | player | Who am I |
| `POST /game/start/` | player | New run → first puzzle |
| `GET /game/active/` | player | Resume an unfinished run |
| `POST /game/answer/` | player | Submit an answer (`round_id`, `answer`) |
| `POST /game/next/` | player | Retry the next puzzle after a hiccup |
| `GET /leaderboard/` | public | Best completed score per player |
| `GET /events/stream/` | public | SSE live leaderboard updates |
| `GET /health/` | public | Server + database check |

## Where each thing lives

```text
backend/
  accounts/models.py     Player table (name, email, password)
  game/models.py         GameSession + Round tables
  game/banana.py         the one place that talks to the external API
  game/services.py       game rules: start, answer, leaderboard
  events/broker.py       in-memory pub/sub
  events/views.py        SSE stream endpoint
frontend/
  src/pages/             Play, Leaderboard, Login, Register
  src/lib/api.ts         one fetch helper + the API calls
  src/lib/auth.tsx       login state (React context)
```

## Tests

```bash
cd backend && .venv/bin/python manage.py test
cd frontend && npm run lint && npm run build

```

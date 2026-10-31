// Types mirror the Django API responses 1:1.

export interface Player {
  id: string
  name: string
  email: string
  date_joined: string
}

export interface Tokens {
  access: string
  refresh: string
}

export interface AuthResponse {
  player: Player
  tokens: Tokens
}

export interface GameSession {
  id: string
  score: number
  rounds_played: number
  total_rounds: number
}

export interface Round {
  id: string
  index: number
  image_url: string
  served_at: string
}

export interface AnswerResponse {
  result: {
    correct: boolean
    correct_answer: number
    player_answer: number | null
    points: number
  }
  session: GameSession
  next_round: Round | null
  needs_next: boolean
  finished: { score: number; played_at: string } | null
}

export interface StartResponse {
  session: GameSession
  round: Round
}

export interface LeaderboardEntry {
  rank: number
  score: number
  name: string
}

export interface LeaderboardResponse {
  entries: LeaderboardEntry[]
}

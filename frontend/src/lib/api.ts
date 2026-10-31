import type {
  AnswerResponse,
  AuthResponse,
  LeaderboardResponse,
  Round,
  StartResponse,
} from '../types'

const API_BASE = (import.meta.env.VITE_API_URL ?? '/api').replace(/\/$/, '')
export { API_BASE }

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

// ---- tokens (localStorage) ------------------------------------------------

const TOKENS_KEY = 'banana.tokens'

export function getTokens() {
  try {
    const raw = localStorage.getItem(TOKENS_KEY)
    return raw ? (JSON.parse(raw) as { access: string; refresh: string }) : null
  } catch {
    return null
  }
}

export function setTokens(tokens: { access: string; refresh: string }) {
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
}

export function clearTokens() {
  localStorage.removeItem(TOKENS_KEY)
}

// ---- one fetch helper -----------------------------------------------------

async function request<T>(path: string, body?: unknown, retried = false): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const tokens = getTokens()
  if (tokens) headers.Authorization = `Bearer ${tokens.access}`

  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError('Cannot reach the game server. Is the backend running?', 0)
  }

  // Access token expired → refresh once and retry.
  if (response.status === 401 && tokens && !retried) {
    const refreshed = await fetch(`${API_BASE}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: tokens.refresh }),
    })
    if (refreshed.ok) {
      const data = (await refreshed.json()) as { access: string }
      setTokens({ access: data.access, refresh: tokens.refresh })
      return request<T>(path, body, true)
    }
    clearTokens()
    window.dispatchEvent(new Event('banana:logout'))
  }

  if (!response.ok) {
    let message = 'Something went wrong. Please try again.'
    try {
      const payload = await response.json()
      if (payload?.error?.message) message = payload.error.message
      else if (payload?.detail) message = payload.detail
    } catch {
      // non-JSON error body
    }
    throw new ApiError(message, response.status)
  }

  return (await response.json()) as T
}

// ---- the API the pages use ------------------------------------------------

export const api = {
  register: (payload: { name: string; email: string; password: string }) =>
    request<AuthResponse>('/auth/register/', payload),
  login: async (payload: { email: string; password: string }) => {
    // SimpleJWT puts access/refresh at the top level; normalise here.
    const data = await request<{
      access: string
      refresh: string
      player: AuthResponse['player']
    }>('/auth/login/', payload)
    return { player: data.player, tokens: { access: data.access, refresh: data.refresh } }
  },
  me: () => request<{ player: AuthResponse['player'] }>('/auth/me/'),

  game: {
    start: () => request<StartResponse>('/game/start/', {}),
    active: () => request<{ session: StartResponse['session'] | null; round: Round | null }>('/game/active/'),
    answer: (payload: { round_id: string; answer: number }) =>
      request<AnswerResponse>('/game/answer/', payload),
    next: () => request<{ round: Round }>('/game/next/', {}),
  },

  leaderboard: () => request<LeaderboardResponse>('/leaderboard/'),
}

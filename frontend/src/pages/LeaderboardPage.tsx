import { useEffect, useState } from 'react'
import { api, API_BASE, ApiError } from '../lib/api'
import type { LeaderboardEntry } from '../types'

export function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [live, setLive] = useState(false)

  function load() {
    api
      .leaderboard()
      .then((data) => setEntries(data.entries))
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : 'Load failed.'))
  }

  useEffect(() => {
    load()

    // Server-Sent Events: when any run finishes, the server pushes an event
    // and the board reloads without the visitor doing anything.
    const stream = new EventSource(`${API_BASE}/events/stream/`)
    stream.addEventListener('connected', () => setLive(true))
    stream.addEventListener('leaderboard.updated', load)
    stream.onerror = () => setLive(false)
    return () => stream.close()
  }, [])

  return (
    <div className="container page narrow">
      <div className="card">
        <div className="toolbar">
          <h1>Leaderboard</h1>
          <span className={live ? 'badge live' : 'badge'}>{live ? 'Live' : 'Reconnecting…'}</span>
        </div>
        <p className="muted">All-time best completed runs. Updates on its own.</p>
        {error && <p className="error">{error}</p>}
        {!entries && !error && <p className="muted">Loading…</p>}
        {entries && entries.length === 0 && <p className="muted">No finished runs yet. Be the first!</p>}
        {entries && entries.length > 0 && (
          <table className="board">
            <thead>
              <tr>
                <th>#</th>
                <th>Player</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.rank}>
                  <td>{entry.rank}</td>
                  <td>{entry.name}</td>
                  <td>{entry.score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

import { Link } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export function Navbar() {
  const { player, loading, logout } = useAuth()

  return (
    <header className="nav">
      <div className="container nav-inner">
        <Link to="/play" className="brand">
          <strong>Banana Blitz</strong>
        </Link>

        <nav className="nav-links">
          <Link to="/play">Play</Link>
          <Link to="/leaderboard">Leaderboard</Link>
        </nav>

        <div className="nav-actions">
          {loading ? (
            <span className="muted">…</span>
          ) : player ? (
            <>
              <span>{player.name}</span>
              <button type="button" className="btn ghost" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn ghost">Log in</Link>
              <Link to="/register" className="btn">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

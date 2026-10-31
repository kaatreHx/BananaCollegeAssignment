import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await register(name, email, password)
      navigate('/play')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Registration failed. Try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container page narrow">
      <div className="card">
        <h1>Create account</h1>
        <form onSubmit={handleSubmit} className="form">
          <label>
            Name
            <input value={name} required onChange={(event) => setName(event.target.value)} />
          </label>
          <label>
            Email
            <input
              type="email"
              value={email}
              required
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              required
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn" disabled={busy}>
            {busy ? 'Creating…' : 'Sign up'}
          </button>
        </form>
        <p className="muted">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  )
}

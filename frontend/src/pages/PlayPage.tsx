import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader } from '../components/Loader'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import type { GameSession, Round } from '../types'

type Stage = 'loading' | 'ready' | 'playing' | 'over'

export function PlayPage() {
  const { player } = useAuth()
  const [stage, setStage] = useState<Stage>('loading')
  const [session, setSession] = useState<GameSession | null>(null)
  const [round, setRound] = useState<Round | null>(null)
  const [answer, setAnswer] = useState('')
  const [popup, setPopup] = useState<{ text: string; good: boolean } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const submitting = useRef(false)

  // On load: is there an unfinished run to resume?
  useEffect(() => {
    if (!player) return
    api.game
      .active()
      .then((data) => {
        if (data.session && data.round) {
          setSession(data.session)
          setRound(data.round)
          setStage('playing')
        } else {
          setStage('ready')
        }
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : 'Could not load the game.')
        setStage('ready')
      })
  }, [player])

  async function startGame() {
    setBusy(true)
    setError(null)
    try {
      const data = await api.game.start()
      setSession(data.session)
      setRound(data.round)
      setAnswer('')
      setPopup(null)
      setStage('playing')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not start the run.')
    } finally {
      setBusy(false)
    }
  }

  async function submit() {
    if (!session || !round || submitting.current) return
    submitting.current = true
    setBusy(true)
    setError(null)
    try {
      const data = await api.game.answer({ round_id: round.id, answer: Number(answer) })
      setSession(data.session)
      setAnswer('')
      // Popup: show right/wrong for a moment, then move on.
      setPopup(data.result.correct
        ? { text: 'Correct! 🍌 +1 point', good: true }
        : { text: `Wrong — the answer was ${data.result.correct_answer}`, good: false })
      const advance = () => {
        setPopup(null)
        submitting.current = false
        if (data.finished) {
          setStage('over')
        } else if (data.next_round) {
          setRound(data.next_round)
        } else {
          // next_round is only null on a puzzle-service hiccup: retry it.
          api.game.next().then((retry) => {
            setRound(retry.round)
          }).catch(() => setError('Could not load the next puzzle. Click Start run to retry.'))
        }
      }
      setTimeout(advance, 1200)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not submit the answer.')
      setBusy(false)
      submitting.current = false
    } finally {
      setBusy(false)
    }
  }

  if (stage === 'loading') {
    return (
      <div className="container page">
        <Loader label="Checking for your run…" />
      </div>
    )
  }

  if (stage === 'ready') {
    return (
      <div className="container page narrow">
        <div className="card center">
          <h1>Play the banana puzzle</h1>
          <p className="muted">
            10 puzzles per run · 1 point per correct answer
          </p>
          {error && <p className="error">{error}</p>}
          <button type="button" className="btn" disabled={busy} onClick={() => void startGame()}>
            {busy ? 'Starting…' : 'Start run'}
          </button>
          <p className="muted">
            <Link to="/leaderboard">View the leaderboard</Link>
          </p>
        </div>
      </div>
    )
  }

  if (stage === 'over') {
    return (
      <div className="container page narrow">
        <div className="card center">
          <h1>Run over 🍌</h1>
          <p className="big-score">{session?.score} points</p>
          <p className="muted">Your score is on the public leaderboard.</p>
          <div className="actions">
            <button type="button" className="btn" onClick={() => void startGame()}>
              Play again
            </button>
            <Link to="/leaderboard" className="btn ghost">
              Leaderboard
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // stage === 'playing'
  return (
    <div className="container page narrow">
      <div className="card center">
        <div className="toolbar">
          <span>
            Round {round?.index} / {session?.total_rounds}
          </span>
          <span>Score: {session?.score}</span>
        </div>
        {round && (
          <img src={round.image_url} alt="Banana puzzle" className="puzzle" />
        )}
        <p className="eyebrow">What is the banana worth?</p>
        {error && <p className="error">{error}</p>}
        <form
          className="form inline"
          onSubmit={(event) => {
            event.preventDefault()
            void submit()
          }}
        >
          <input
            type="number"
            min={0}
            max={999}
            placeholder="Your answer"
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            required
          />
          <button type="submit" className="btn" disabled={busy}>
            {busy ? 'Checking…' : 'Submit'}
          </button>
        </form>
      </div>
      {popup && (
        <div className={`popup ${popup.good ? 'good' : 'bad'}`}>
          {popup.text}
        </div>
      )}
    </div>
  )
}

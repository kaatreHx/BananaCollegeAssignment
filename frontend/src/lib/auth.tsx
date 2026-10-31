import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api, clearTokens, getTokens, setTokens } from './api'
import type { Player } from '../types'

interface AuthValue {
  player: Player | null
  loading: boolean
  login: (email: string, password: string) => Promise<Player>
  register: (name: string, email: string, password: string) => Promise<Player>
  logout: () => void
}

const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [player, setPlayer] = useState<Player | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getTokens()) {
      setLoading(false)
      return
    }
    api
      .me()
      .then(({ player: fresh }) => setPlayer(fresh))
      .catch(() => clearTokens())
      .finally(() => setLoading(false))
  }, [])

  const value: AuthValue = {
    player,
    loading,
    login: async (email, password) => {
      const response = await api.login({ email, password })
      setTokens(response.tokens)
      setPlayer(response.player)
      return response.player
    },
    register: async (name, email, password) => {
      const response = await api.register({ name, email, password })
      setTokens(response.tokens)
      setPlayer(response.player)
      return response.player
    },
    logout: () => {
      clearTokens()
      setPlayer(null)
    },
  }

  // Any page can listen: token refresh failed → log out everywhere.
  useEffect(() => {
    const handle = () => setPlayer(null)
    window.addEventListener('banana:logout', handle)
    return () => window.removeEventListener('banana:logout', handle)
  }, [])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>.')
  return context
}

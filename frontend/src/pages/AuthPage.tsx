import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { Button } from '../components/Button'
import { Input, Label } from '../components/Input'

export function AuthPage() {
  const { session, signUp, signIn } = useAuth()
  const [mode, setMode] = useState<'sign-in' | 'sign-up'>('sign-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setInfo(null)
    setSubmitting(true)

    const result =
      mode === 'sign-up' ? await signUp(email, password) : await signIn(email, password)

    setSubmitting(false)

    if (result.error) {
      setError(result.error)
      return
    }

    if (mode === 'sign-up') {
      setInfo('Check your email to confirm your account, then sign in.')
    }
  }

  if (session) return <Navigate to="/feed" replace />

  return (
    <div className="flex min-h-svh items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-sm rounded-xl border border-line bg-surface p-6 shadow-sm">
        <h1 className="mb-1 text-lg font-semibold text-ink">
          {mode === 'sign-in' ? 'Sign in' : 'Create your account'}
        </h1>
        <p className="mb-6 text-sm text-ink-muted">
          Job Finder finds matching postings and notifies you — nothing more.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Email</Label>
            <Input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>
          <div>
            <Label>Password</Label>
            <Input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'sign-in' ? 'current-password' : 'new-password'}
            />
          </div>

          {error && <p className="text-sm text-error">{error}</p>}
          {info && <p className="text-sm text-success">{info}</p>}

          <Button type="submit" disabled={submitting} className="w-full">
            {mode === 'sign-in' ? 'Sign in' : 'Sign up'}
          </Button>
        </form>

        <button
          type="button"
          onClick={() => {
            setMode(mode === 'sign-in' ? 'sign-up' : 'sign-in')
            setError(null)
            setInfo(null)
          }}
          className="mt-4 w-full text-center text-sm text-ink-muted hover:text-ink"
        >
          {mode === 'sign-in'
            ? "Don't have an account? Sign up"
            : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  )
}

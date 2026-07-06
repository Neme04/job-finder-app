import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import type { Session, User } from '@supabase/supabase-js'
import { supabase } from './supabase'
import type { Profile } from '../types/db'

interface AuthContextValue {
  session: Session | null
  user: User | null
  profile: Profile | null
  loading: boolean
  signUp: (email: string, password: string) => Promise<{ error: string | null }>
  signIn: (email: string, password: string) => Promise<{ error: string | null }>
  signOut: () => Promise<void>
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

async function ensureProfile(userId: string): Promise<Profile | null> {
  const { data: existing } = await supabase
    .from('profiles')
    .select('*')
    .eq('user_id', userId)
    .maybeSingle()

  if (existing) return existing as Profile

  const { data: created, error } = await supabase
    .from('profiles')
    .insert({ user_id: userId })
    .select()
    .single()

  if (error) {
    console.error('Failed to create profile', error)
    return null
  }
  return created as Profile
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const lastLoadedToken = useRef<string | null>(null)

  const loadProfile = async (userId: string) => {
    const p = await ensureProfile(userId)
    setProfile(p)
  }

  useEffect(() => {
    supabase.auth.getSession().then(async ({ data }) => {
      setSession(data.session)
      if (data.session?.user) {
        lastLoadedToken.current = data.session.access_token
        await loadProfile(data.session.user.id)
      }
      setLoading(false)
    })

    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession)
      if (!newSession?.user) {
        lastLoadedToken.current = null
        setProfile(null)
        return
      }
      // GoTrue can re-emit SIGNED_IN for the same, unchanged session (e.g. on
      // every request while a query is in flight); re-fetching the profile
      // each time creates a feedback loop. Only load once per distinct token.
      if (lastLoadedToken.current === newSession.access_token) return
      lastLoadedToken.current = newSession.access_token

      const userId = newSession.user.id
      // Deferred: awaiting another Supabase call directly inside this
      // callback can deadlock/re-fire the listener (Supabase JS gotcha).
      setTimeout(() => {
        loadProfile(userId)
      }, 0)
    })

    return () => listener.subscription.unsubscribe()
  }, [])

  const signUp = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({ email, password })
    return { error: error?.message ?? null }
  }

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    return { error: error?.message ?? null }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
  }

  const refreshProfile = async () => {
    if (session?.user) await loadProfile(session.user.id)
  }

  return (
    <AuthContext.Provider
      value={{
        session,
        user: session?.user ?? null,
        profile,
        loading,
        signUp,
        signIn,
        signOut,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

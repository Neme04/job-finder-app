import { useAuth } from '../lib/auth'
import { useTheme } from '../lib/theme'
import { supabase } from '../lib/supabase'
import { Button } from '../components/Button'
import { Toggle } from '../components/Toggle'

export function Settings() {
  const { profile, signOut, refreshProfile } = useAuth()
  const { theme, toggleTheme } = useTheme()

  if (!profile) return <p className="text-sm text-ink-muted">Loading…</p>

  const updateNotify = async (field: 'notify_email' | 'notify_whatsapp', value: boolean) => {
    await supabase.from('profiles').update({ [field]: value }).eq('user_id', profile.user_id)
    await refreshProfile()
  }

  return (
    <div className="max-w-md space-y-6">
      <h1 className="text-lg font-semibold text-ink">Settings</h1>

      <section className="space-y-4 rounded-xl border border-line bg-surface p-4">
        <h2 className="text-sm font-semibold text-ink">Notifications</h2>
        <div className="flex items-center justify-between">
          <span className="text-sm text-ink">Email alerts</span>
          <Toggle
            checked={profile.notify_email}
            onChange={(v) => updateNotify('notify_email', v)}
          />
        </div>
        {profile.role === 'admin' && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-ink">WhatsApp alerts</span>
            <Toggle
              checked={profile.notify_whatsapp}
              onChange={(v) => updateNotify('notify_whatsapp', v)}
            />
          </div>
        )}
      </section>

      <section className="space-y-4 rounded-xl border border-line bg-surface p-4">
        <h2 className="text-sm font-semibold text-ink">Appearance</h2>
        <div className="flex items-center justify-between">
          <span className="text-sm text-ink">Dark mode</span>
          <Toggle checked={theme === 'dark'} onChange={toggleTheme} />
        </div>
      </section>

      <Button variant="secondary" onClick={signOut}>
        Sign out
      </Button>
    </div>
  )
}

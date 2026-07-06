import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import { AVAILABLE_SOURCES } from '../lib/sources'
import type { RemotePref, SearchCriteria } from '../types/db'
import { Button } from '../components/Button'
import { Input, Label, Select } from '../components/Input'
import { TagInput } from '../components/TagInput'

const REMOTE_PREFS: { value: RemotePref; label: string }[] = [
  { value: 'any', label: 'Any' },
  { value: 'remote', label: 'Remote only' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'onsite', label: 'Onsite' },
]

export function Criteria() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const [jobTitles, setJobTitles] = useState<string[]>([])
  const [regions, setRegions] = useState<string[]>([])
  const [remotePref, setRemotePref] = useState<RemotePref>('any')
  const [salaryFloor, setSalaryFloor] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [sourcesEnabled, setSourcesEnabled] = useState<string[]>([])

  useEffect(() => {
    if (!user) return
    supabase
      .from('search_criteria')
      .select('*')
      .eq('profile_id', user.id)
      .maybeSingle()
      .then(({ data }) => {
        const criteria = data as SearchCriteria | null
        if (criteria) {
          setJobTitles(criteria.job_titles ?? [])
          setRegions(criteria.regions ?? [])
          setRemotePref(criteria.remote_pref ?? 'any')
          setSalaryFloor(criteria.salary_floor?.toString() ?? '')
          setCurrency(criteria.currency ?? 'USD')
          setSourcesEnabled(criteria.sources_enabled ?? [])
        }
        setLoading(false)
      })
  }, [user])

  const toggleSource = (id: string) => {
    setSourcesEnabled((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id],
    )
  }

  const handleSave = async () => {
    if (!user) return
    setSaving(true)
    setSaved(false)

    await supabase.from('search_criteria').upsert(
      {
        profile_id: user.id,
        job_titles: jobTitles,
        regions,
        remote_pref: remotePref,
        salary_floor: salaryFloor ? Number(salaryFloor) : null,
        currency,
        sources_enabled: sourcesEnabled,
        updated_at: new Date().toISOString(),
      },
      { onConflict: 'profile_id' },
    )

    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  if (loading) {
    return <p className="text-sm text-ink-muted">Loading…</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-ink">Search criteria</h1>
        <p className="text-sm text-ink-muted">
          This is your only setup — edit it anytime and the next sweep picks it up.
        </p>
      </div>

      <div>
        <Label>Job titles / keywords</Label>
        <TagInput
          tags={jobTitles}
          onChange={setJobTitles}
          placeholder="e.g. product designer, brand designer"
        />
      </div>

      <div>
        <Label>Regions</Label>
        <TagInput
          tags={regions}
          onChange={setRegions}
          placeholder="e.g. remote, nigeria, europe"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Remote preference</Label>
          <Select
            value={remotePref}
            onChange={(e) => setRemotePref(e.target.value as RemotePref)}
          >
            {REMOTE_PREFS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <Label>Salary floor</Label>
          <div className="flex gap-2">
            <Input
              type="number"
              min={0}
              value={salaryFloor}
              onChange={(e) => setSalaryFloor(e.target.value)}
              placeholder="Optional"
            />
            <Select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-24"
            >
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="NGN">NGN</option>
            </Select>
          </div>
        </div>
      </div>

      <div>
        <Label>Sources to sweep</Label>
        <p className="mb-2 text-xs text-ink-faint">
          Leave all unchecked to sweep every available source.
        </p>
        <div className="flex flex-wrap gap-2">
          {AVAILABLE_SOURCES.map((source) => {
            const active = sourcesEnabled.includes(source.id)
            return (
              <button
                key={source.id}
                type="button"
                onClick={() => toggleSource(source.id)}
                className={`rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                  active
                    ? 'border-brand bg-brand-subtle text-brand'
                    : 'border-line bg-surface text-ink-muted hover:bg-surface-hover'
                }`}
              >
                {source.label}
              </button>
            )
          })}
        </div>
      </div>

      <div className="flex items-center gap-3 pt-2">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving…' : 'Save criteria'}
        </Button>
        {saved && <span className="text-sm text-success">Saved</span>}
      </div>
    </div>
  )
}

import { useEffect, useMemo, useState } from 'react'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import type { JobStatus, UserJob } from '../types/db'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { Input } from '../components/Input'

const TABS: { value: JobStatus; label: string }[] = [
  { value: 'new', label: 'New' },
  { value: 'saved', label: 'Saved' },
  { value: 'applied', label: 'Applied' },
  { value: 'skipped', label: 'Skipped' },
]

function formatSalary(min: number | null, max: number | null, currency: string | null) {
  if (!min && !max) return null
  const cur = currency ?? ''
  if (min && max) return `${cur} ${min.toLocaleString()}–${max.toLocaleString()}`
  return `${cur} ${(min ?? max)!.toLocaleString()}+`
}

function formatDate(value: string | null) {
  if (!value) return null
  return new Date(value).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  })
}

export function Feed() {
  const { user } = useAuth()
  const [rows, setRows] = useState<UserJob[]>([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<JobStatus>('new')
  const [search, setSearch] = useState('')

  const load = async () => {
    if (!user) return
    setLoading(true)
    const { data } = await supabase
      .from('user_jobs')
      .select('*, jobs(*)')
      .eq('profile_id', user.id)
      .order('created_at', { ascending: false })
    setRows((data as UserJob[]) ?? [])
    setLoading(false)
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  const updateStatus = async (id: string, status: JobStatus) => {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, status } : r)))
    await supabase.from('user_jobs').update({ status }).eq('id', id)
  }

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return rows
      .filter((r) => r.status === tab)
      .filter((r) => {
        if (!q) return true
        const job = r.jobs
        return (
          job.title.toLowerCase().includes(q) ||
          job.company.toLowerCase().includes(q) ||
          (job.location ?? '').toLowerCase().includes(q)
        )
      })
  }, [rows, tab, search])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-ink">Feed</h1>
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search title, company, location…"
          className="max-w-xs"
        />
      </div>

      <div className="flex gap-1 border-b border-line">
        {TABS.map((t) => (
          <button
            key={t.value}
            onClick={() => setTab(t.value)}
            className={`border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
              tab === t.value
                ? 'border-brand text-brand'
                : 'border-transparent text-ink-muted hover:text-ink'
            }`}
          >
            {t.label}
            <span className="ml-1.5 text-xs text-ink-faint">
              {rows.filter((r) => r.status === t.value).length}
            </span>
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-ink-muted">Loading…</p>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-ink-muted">No jobs here yet.</p>
      ) : (
        <ul className="space-y-3">
          {filtered.map((row) => {
            const job = row.jobs
            const salary = formatSalary(job.salary_min, job.salary_max, job.currency)
            const posted = formatDate(job.posted_at)
            return (
              <li
                key={row.id}
                className="rounded-xl border border-line bg-surface p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="truncate text-sm font-semibold text-ink">
                        {job.title}
                      </h2>
                      {job.remote && <Badge tone="info">Remote</Badge>}
                      <Badge tone="neutral">{job.source_id}</Badge>
                    </div>
                    <p className="mt-0.5 text-sm text-ink-muted">
                      {job.company}
                      {job.location ? ` · ${job.location}` : ''}
                    </p>
                    <div className="mt-1 flex flex-wrap gap-x-3 text-xs text-ink-faint">
                      {salary && <span>{salary}</span>}
                      {posted && <span>Posted {posted}</span>}
                    </div>
                  </div>
                  <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0"
                  >
                    <Button variant="primary">Apply</Button>
                  </a>
                </div>

                <div className="mt-3 flex gap-2">
                  <Button
                    variant={row.status === 'saved' ? 'secondary' : 'ghost'}
                    onClick={() => updateStatus(row.id, 'saved')}
                    className="text-xs"
                  >
                    Save
                  </Button>
                  <Button
                    variant={row.status === 'applied' ? 'secondary' : 'ghost'}
                    onClick={() => updateStatus(row.id, 'applied')}
                    className="text-xs"
                  >
                    Mark applied
                  </Button>
                  <Button
                    variant={row.status === 'skipped' ? 'secondary' : 'ghost'}
                    onClick={() => updateStatus(row.id, 'skipped')}
                    className="text-xs"
                  >
                    Skip
                  </Button>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}

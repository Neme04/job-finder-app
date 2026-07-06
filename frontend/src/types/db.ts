export type Role = 'user' | 'admin'
export type RemotePref = 'remote' | 'hybrid' | 'onsite' | 'any'
export type JobStatus = 'new' | 'saved' | 'applied' | 'skipped'

export interface Profile {
  user_id: string
  role: Role
  full_name: string | null
  notify_email: boolean
  notify_whatsapp: boolean
  created_at: string
}

export interface SearchCriteria {
  id: string
  profile_id: string
  job_titles: string[]
  regions: string[]
  remote_pref: RemotePref
  salary_floor: number | null
  currency: string
  sources_enabled: string[]
  updated_at: string
}

export interface Job {
  id: string
  canonical_key: string
  source_id: string
  external_id: string
  title: string
  company: string
  location: string | null
  remote: boolean
  description: string | null
  apply_url: string
  salary_min: number | null
  salary_max: number | null
  currency: string | null
  posted_at: string | null
  first_seen: string
  last_seen: string
}

export interface UserJob {
  id: string
  profile_id: string
  job_id: string
  status: JobStatus
  notified_at: string | null
  created_at: string
  jobs: Job
}

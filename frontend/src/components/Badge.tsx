type Tone = 'brand' | 'success' | 'warning' | 'error' | 'info' | 'neutral'

const toneClasses: Record<Tone, string> = {
  brand: 'bg-brand-subtle text-brand',
  success: 'bg-success-subtle text-success',
  warning: 'bg-warning-subtle text-warning',
  error: 'bg-error-subtle text-error',
  info: 'bg-info-subtle text-info',
  neutral: 'bg-surface-hover text-ink-muted',
}

export function Badge({
  tone = 'neutral',
  children,
}: {
  tone?: Tone
  children: React.ReactNode
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${toneClasses[tone]}`}
    >
      {children}
    </span>
  )
}

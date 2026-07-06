import { NavLink } from 'react-router-dom'
import { useTheme } from '../lib/theme'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive ? 'bg-brand-subtle text-brand' : 'text-ink-muted hover:bg-surface-hover hover:text-ink'
  }`

export function NavBar() {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <span className="text-sm font-semibold text-ink">Job Finder</span>
        <nav className="flex items-center gap-1">
          <NavLink to="/feed" className={linkClass}>
            Feed
          </NavLink>
          <NavLink to="/criteria" className={linkClass}>
            Criteria
          </NavLink>
          <NavLink to="/settings" className={linkClass}>
            Settings
          </NavLink>
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="ml-2 rounded-lg border border-line px-3 py-2 text-sm text-ink-muted hover:bg-surface-hover"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </nav>
      </div>
    </header>
  )
}

export default function AppHeader({ session, onLogout }) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-teal-700">
            TechKraft
          </p>
          <h1 className="text-xl font-semibold">Candidate review dashboard</h1>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="hidden text-slate-600 sm:inline">
            {session.user.email} · {session.user.role}
          </span>
          <button className="border border-slate-300 px-3 py-2" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

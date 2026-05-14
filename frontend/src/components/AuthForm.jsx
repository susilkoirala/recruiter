export default function AuthForm({
  authMode,
  authForm,
  authError,
  loadingAuth,
  onSubmit,
  onChange,
  onToggleMode,
}) {
  return (
    <div className="border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-teal-700">TechKraft Recruiter</p>
      <h1 className="mt-2 text-2xl font-semibold">
        {authMode === 'login' ? 'Sign in' : 'Create reviewer account'}
      </h1>
      <form className="mt-6 space-y-4" onSubmit={onSubmit}>
        <label className="block text-sm font-medium">
          Email
          <input
            className="mt-1 w-full border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
            type="email"
            value={authForm.email}
            onChange={(event) => onChange({ ...authForm, email: event.target.value })}
            required
          />
        </label>
        <label className="block text-sm font-medium">
          Password
          <input
            className="mt-1 w-full border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
            type="password"
            value={authForm.password}
            onChange={(event) => onChange({ ...authForm, password: event.target.value })}
            minLength={authMode === 'register' ? 8 : 1}
            required
          />
        </label>
        {authError && <p className="text-sm text-red-700">{authError}</p>}
        <button
          className="w-full bg-slate-950 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          disabled={loadingAuth}
        >
          {loadingAuth ? 'Working...' : authMode === 'login' ? 'Sign in' : 'Register'}
        </button>
      </form>
      <button
        className="mt-4 text-sm font-medium text-teal-700"
        type="button"
        onClick={onToggleMode}
      >
        {authMode === 'login' ? 'Register as reviewer' : 'Use existing account'}
      </button>
    </div>
  )
}

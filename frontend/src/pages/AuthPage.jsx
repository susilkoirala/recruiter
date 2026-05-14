import { useState } from 'react'

import { requestAuth } from '../api/client'
import AuthForm from '../components/AuthForm'

export default function AuthPage({ onAuthenticated }) {
  const [authMode, setAuthMode] = useState('login')
  const [authForm, setAuthForm] = useState({ email: '', password: '' })
  const [authError, setAuthError] = useState('')
  const [loadingAuth, setLoadingAuth] = useState(false)

  async function handleAuth(event) {
    event.preventDefault()
    setLoadingAuth(true)
    setAuthError('')

    try {
      const session = await requestAuth(authMode, authForm)
      onAuthenticated(session)
      setAuthForm({ email: '', password: '' })
    } catch (error) {
      setAuthError(error.message)
    } finally {
      setLoadingAuth(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <section className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-5">
        <AuthForm
          authMode={authMode}
          authForm={authForm}
          authError={authError}
          loadingAuth={loadingAuth}
          onSubmit={handleAuth}
          onChange={setAuthForm}
          onToggleMode={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
        />
      </section>
    </main>
  )
}

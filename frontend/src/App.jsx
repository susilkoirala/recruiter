import { useState } from 'react'

import { readSession, saveSession } from './api/session'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  const [session, setSession] = useState(readSession)

  function updateSession(nextSession) {
    setSession(nextSession)
    saveSession(nextSession)
  }

  if (!session) {
    return <AuthPage onAuthenticated={updateSession} />
  }

  return <DashboardPage session={session} onSessionChange={updateSession} />
}

export default App

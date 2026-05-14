import { useState } from 'react'

import { readSession, saveSession } from './api/session'
import AuthPage from './pages/AuthPage'

function App() {
  const [session, setSession] = useState(readSession)

  function updateSession(nextSession) {
    setSession(nextSession)
    saveSession(nextSession)
  }

  if (!session) {
    return <AuthPage onAuthenticated={updateSession} />
  }

}

export default App

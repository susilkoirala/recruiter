export const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export function getScoreStreamUrl(candidateId, accessToken) {
  const params = new URLSearchParams({ token: accessToken })
  return `${API_BASE}/candidates/${candidateId}/stream?${params.toString()}`
}

export async function requestAuth(mode, payload) {
  const response = await fetch(`${API_BASE}/auth/${mode}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return parseResponse(response, 'Authentication failed')
}

export async function requestLogout(refreshToken) {
  if (!refreshToken) return

  await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  }).catch(() => {})
}

export function createApiClient(session, updateSession) {
  async function apiFetch(path, options = {}, retry = true) {
    const headers = {
      'Content-Type': 'application/json',
      ...(session?.access_token
        ? { Authorization: `Bearer ${session.access_token}` }
        : {}),
      ...(options.headers || {}),
    }

    let response = await fetch(`${API_BASE}${path}`, { ...options, headers })
    if (response.status === 401 && retry && session?.refresh_token) {
      const refreshed = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: session.refresh_token }),
      })

      if (refreshed.ok) {
        const nextSession = await refreshed.json()
        updateSession(nextSession)
        response = await fetch(`${API_BASE}${path}`, {
          ...options,
          headers: {
            ...headers,
            Authorization: `Bearer ${nextSession.access_token}`,
          },
        })
      } else {
        updateSession(null)
      }
    }

    return parseResponse(response)
  }

  return {
    listCandidates(params) {
      return apiFetch(`/candidates?${params.toString()}`)
    },
    getCandidateOptions() {
      return apiFetch('/candidates/options')
    },
    getCandidate(id) {
      return apiFetch(`/candidates/${id}`)
    },
    createCandidate(payload) {
      return apiFetch('/candidates', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    },
    updateCandidate(id, payload) {
      return apiFetch(`/candidates/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
    },
    createScore(candidateId, payload) {
      return apiFetch(`/candidates/${candidateId}/scores`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    },
    generateSummary(candidateId) {
      return apiFetch(`/candidates/${candidateId}/summary`, { method: 'POST' })
    },
  }
}

async function parseResponse(response, fallback = 'Request failed') {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || fallback)
  }

  if (response.status === 204) return null
  return response.json()
}

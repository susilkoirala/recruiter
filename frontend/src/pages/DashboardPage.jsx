import { useEffect, useMemo, useState } from 'react'

import { createApiClient, getScoreStreamUrl, requestLogout } from '../api/client'
import AppHeader from '../components/AppHeader'
import CandidateCreateForm, {
  emptyCandidateForm,
} from '../components/CandidateCreateForm'
import CandidateFilters from '../components/CandidateFilters'
import CandidateList from '../components/CandidateList'
import Modal from '../components/Modal'
import CandidateDetailPage from './CandidateDetailPage'

const PAGE_SIZE = 20
const emptyFilters = {
  status: '',
  role_applied: '',
  skill: '',
  keyword: '',
}

function getCandidateIdFromPath() {
  const match = window.location.pathname.match(/^\/candidates\/(\d+)$/)
  return match ? Number(match[1]) : null
}

export default function DashboardPage({ session, onSessionChange }) {
  const initialCandidateId = getCandidateIdFromPath()
  const [view, setView] = useState(initialCandidateId ? 'detail' : 'list')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [options, setOptions] = useState({ roles: [], skills: [], statuses: [] })
  const [filters, setFilters] = useState(emptyFilters)
  const [page, setPage] = useState(1)
  const [candidates, setCandidates] = useState([])
  const [selectedId, setSelectedId] = useState(initialCandidateId)
  const [selectedCandidate, setSelectedCandidate] = useState(null)
  const [loadingList, setLoadingList] = useState(false)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [message, setMessage] = useState('')

  const [scoreForm, setScoreForm] = useState({ category: '', score: 3, note: '' })
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [notesDraft, setNotesDraft] = useState('')
  const [statusDraft, setStatusDraft] = useState('new')
  const [candidateForm, setCandidateForm] = useState(emptyCandidateForm)
  const [streamStatus, setStreamStatus] = useState('Disconnected')
  const [didLoadInitialCandidates, setDidLoadInitialCandidates] = useState(false)

  const isAdmin = session?.user?.role === 'admin'
  const api = useMemo(
    () => createApiClient(session, onSessionChange),
    [session, onSessionChange],
  )

  async function logout() {
    await requestLogout(session?.refresh_token)
    onSessionChange(null)
    setSelectedCandidate(null)
    setCandidates([])
    window.history.replaceState({}, '', '/')
  }

  function openCandidate(id) {
    setSelectedId(id)
    setView('detail')
    window.history.pushState({}, '', `/candidates/${id}`)
  }

  function openList() {
    setView('list')
    window.history.pushState({}, '', '/')
  }

  function clearFilters() {
    setFilters(emptyFilters)
    setPage(1)
    loadCandidates(1, emptyFilters)
  }

  async function loadOptions() {
    try {
      setOptions(await api.getCandidateOptions())
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function loadCandidates(pageOverride = page, filtersOverride = filters) {
    setLoadingList(true)
    setMessage('')

    const params = new URLSearchParams({
      skip: String((pageOverride - 1) * PAGE_SIZE),
      limit: String(PAGE_SIZE),
    })
    Object.entries(filtersOverride).forEach(([key, value]) => {
      if (value) params.set(key, value)
    })

    try {
      const data = await api.listCandidates(params)
      setCandidates(data)
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoadingList(false)
    }
  }

  async function loadCandidateDetail(id = selectedId) {
    if (!id) return
    setLoadingDetail(true)
    setMessage('')

    try {
      const data = await api.getCandidate(id)
      setSelectedCandidate(data)
      setNotesDraft(data.internal_notes || '')
      setStatusDraft(data.status || 'new')
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoadingDetail(false)
    }
  }

  async function submitScore(event) {
    event.preventDefault()
    if (!selectedCandidate) return

    try {
      await api.createScore(selectedCandidate.id, {
        category: scoreForm.category,
        score: Number(scoreForm.score),
        note: scoreForm.note || null,
      })
      setScoreForm({ category: '', score: 3, note: '' })
      await loadCandidateDetail(selectedCandidate.id)
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function generateSummary() {
    if (!selectedCandidate) return
    setSummaryLoading(true)
    setMessage('')

    try {
      await api.generateSummary(selectedCandidate.id)
      await loadCandidateDetail(selectedCandidate.id)
    } catch (error) {
      setMessage(error.message)
    } finally {
      setSummaryLoading(false)
    }
  }

  async function saveNotes() {
    if (!selectedCandidate) return

    try {
      await api.updateCandidate(selectedCandidate.id, { internal_notes: notesDraft })
      await loadCandidateDetail(selectedCandidate.id)
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function saveStatus() {
    if (!selectedCandidate) return

    try {
      await api.updateCandidate(selectedCandidate.id, { status: statusDraft })
      await loadCandidateDetail(selectedCandidate.id)
      await loadCandidates()
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function createCandidate(event) {
    event.preventDefault()

    try {
      const created = await api.createCandidate({
        ...candidateForm,
      })
      setCandidateForm(emptyCandidateForm)
      setShowCreateModal(false)
      openCandidate(created.id)
      await loadCandidates()
    } catch (error) {
      setMessage(error.message)
    }
  }

  useEffect(() => {
    loadOptions()
    loadCandidates().finally(() => setDidLoadInitialCandidates(true))
    const handlePopState = () => {
      const candidateId = getCandidateIdFromPath()
      setSelectedId(candidateId)
      setView(candidateId ? 'detail' : 'list')
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  useEffect(() => {
    if (!didLoadInitialCandidates) return
    loadCandidates()
  }, [page, didLoadInitialCandidates])

  useEffect(() => {
    if (view === 'detail') loadCandidateDetail(selectedId)
  }, [selectedId, view])

  useEffect(() => {
    if (!message) return
    const timeout = setTimeout(() => setMessage(''), 5000)
    return () => clearTimeout(timeout)
  }, [message])

  useEffect(() => {
    if (view !== 'detail' || !selectedId || !session?.access_token) return

    const events = new EventSource(getScoreStreamUrl(selectedId, session.access_token))
    setStreamStatus('Connecting')

    events.addEventListener('connected', () => setStreamStatus('Live'))
    events.addEventListener('heartbeat', () => setStreamStatus('Live'))
    events.addEventListener('score_update', () => {
      setStreamStatus('Updated')
      loadCandidateDetail(selectedId)
    })
    events.onerror = () => setStreamStatus('Reconnecting')

    return () => {
      events.close()
      setStreamStatus('Disconnected')
    }
  }, [view, selectedId, session?.access_token])

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <AppHeader session={session} onLogout={logout} />

      <div className="mx-auto max-w-7xl px-4 py-4">
        {view === 'list' && (
          <div className="space-y-4">
            <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
              <div>
                <h2 className="text-2xl font-semibold">Candidates</h2>
                <p className="text-sm text-slate-600">
                  Review candidate profiles, roles, skills, and current status.
                </p>
              </div>
              {isAdmin && (
                <button
                  className="bg-slate-950 px-4 py-2 text-sm font-medium text-white"
                  onClick={() => setShowCreateModal(true)}
                >
                  Create candidate
                </button>
              )}
            </div>

            <CandidateFilters
              filters={filters}
              options={options}
              onChange={setFilters}
              onApply={() => {
                setPage(1)
                loadCandidates(1)
              }}
              onClear={clearFilters}
            />

            {message && (
              <div className="border border-red-200 bg-red-50 px-5 py-3 text-sm text-red-800">
                {message}
              </div>
            )}

            <CandidateList
              candidates={candidates}
              selectedId={selectedId}
              loading={loadingList}
              page={page}
              pageSize={PAGE_SIZE}
              onSelect={openCandidate}
              onPageChange={setPage}
            />
          </div>
        )}

        {view === 'detail' && (
          <CandidateDetailPage
            candidate={selectedCandidate}
            isAdmin={isAdmin}
            loading={loadingDetail}
            message={message}
            streamStatus={streamStatus}
            summaryLoading={summaryLoading}
            notesDraft={notesDraft}
            scoreForm={scoreForm}
            statusDraft={statusDraft}
            onGenerateSummary={generateSummary}
            onNotesChange={setNotesDraft}
            onSaveNotes={saveNotes}
            onScoreChange={setScoreForm}
            onSubmitScore={submitScore}
            onBack={openList}
            onStatusChange={setStatusDraft}
            onSaveStatus={saveStatus}
          />
        )}
      </div>

      {showCreateModal && (
        <Modal title="Create candidate" onClose={() => setShowCreateModal(false)}>
          <CandidateCreateForm
            form={candidateForm}
            options={options}
            onChange={setCandidateForm}
            onSubmit={createCandidate}
          />
        </Modal>
      )}
    </main>
  )
}

import Badge from './Badge'

export default function CandidateDetail({
  candidate,
  isAdmin,
  loading,
  message,
  summaryLoading,
  notesDraft,
  scoreForm,
  statusDraft,
  onGenerateSummary,
  onNotesChange,
  onSaveNotes,
  onScoreChange,
  onSubmitScore,
  onBack,
  onStatusChange,
  onSaveStatus,
}) {
  if (loading) {
    return <p className="p-5 text-sm text-slate-500">Loading candidate...</p>
  }

  if (!candidate) {
    return <p className="p-5 text-sm text-slate-500">Select a candidate to review.</p>
  }

  return (
    <>
      {message && (
        <div className="border-b border-red-200 bg-red-50 px-5 py-3 text-sm text-red-800">
          {message}
        </div>
      )}
      <div className="space-y-5 p-5">
        <CandidateHeader
          candidate={candidate}
          isAdmin={isAdmin}
          statusDraft={statusDraft}
          onBack={onBack}
          onStatusChange={onStatusChange}
          onSaveStatus={onSaveStatus}
        />

        <section className="grid gap-4 md:grid-cols-2">
          <SummaryPanel
            candidate={candidate}
            loading={summaryLoading}
            onGenerate={onGenerateSummary}
          />
          {isAdmin && (
            <NotesPanel
              notesDraft={notesDraft}
              onChange={onNotesChange}
              onSave={onSaveNotes}
            />
          )}
        </section>

        <section className="grid gap-4 md:grid-cols-[1fr_320px]">
          <ScoresPanel scores={candidate.scores || []} isAdmin={isAdmin} />
          <ScoreForm
            candidate={candidate}
            form={scoreForm}
            onChange={onScoreChange}
            onSubmit={onSubmitScore}
          />
        </section>
      </div>
    </>
  )
}

function CandidateHeader({
  candidate,
  isAdmin,
  statusDraft,
  onBack,
  onStatusChange,
  onSaveStatus,
}) {
  return (
    <div className="border-b border-slate-200 pb-5">
      <button className="mb-4 border border-slate-300 px-3 py-2 text-sm" onClick={onBack}>
        Back to candidates
      </button>
      <div className="flex flex-col justify-between gap-3 md:flex-row">
        <div>
          <Badge type="status" value={candidate.status} />
          <h2 className="mt-1 text-2xl font-semibold">{candidate.name}</h2>
          <p className="text-sm text-slate-600">{candidate.email}</p>
        </div>
        <div className="flex flex-col gap-2 text-sm text-slate-600 md:items-end">
          <Badge type="role" value={candidate.role_applied} />
          <div className="flex flex-wrap gap-1 md:justify-end">
            {candidate.skills?.map((skill) => (
              <Badge key={skill} type="skill" value={skill} />
            ))}
          </div>
        </div>
      </div>
      {isAdmin && (
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <select
            className="border border-slate-300 px-3 py-2 text-sm"
            value={statusDraft}
            onChange={(event) => onStatusChange(event.target.value)}
          >
            <option value="new">New</option>
            <option value="reviewed">Reviewed</option>
            <option value="hired">Hired</option>
            <option value="rejected">Rejected</option>
            <option value="archived">Archived</option>
          </select>
          <button
            className="bg-slate-950 px-3 py-2 text-sm font-medium text-white"
            onClick={onSaveStatus}
          >
            Save status
          </button>
        </div>
      )}
    </div>
  )
}

function SummaryPanel({ candidate, loading, onGenerate }) {
  return (
    <div className="border border-slate-200 p-3">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold">AI summary</h3>
        <button
          className="bg-teal-700 px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
          onClick={onGenerate}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-700">
        {loading
          ? 'Generating summary. This simulates a slow AI call.'
          : candidate.ai_summary || 'No summary generated yet.'}
      </p>
    </div>
  )
}

function NotesPanel({ notesDraft, onChange, onSave }) {
  return (
    <div className="border border-slate-200 p-3">
      <h3 className="font-semibold">Internal notes</h3>
      <textarea
        className="mt-2 min-h-24 w-full border border-slate-300 px-3 py-2 text-sm"
        value={notesDraft}
        onChange={(event) => onChange(event.target.value)}
      />
      <button
        className="mt-2 bg-slate-950 px-3 py-2 text-sm font-medium text-white"
        onClick={onSave}
      >
        Save notes
      </button>
    </div>
  )
}

function ScoresPanel({ scores, isAdmin }) {
  return (
    <div className="border border-slate-200">
      <div className="border-b border-slate-200 px-3 py-2">
        <h3 className="font-semibold">
          Scores {isAdmin ? '(all reviewers)' : '(your scores)'}
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2 font-semibold">Skill</th>
              <th className="px-3 py-2 font-semibold">Score</th>
              {isAdmin && <th className="px-3 py-2 font-semibold">Reviewer</th>}
              <th className="px-3 py-2 font-semibold">Note</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {scores.map((score) => (
              <tr key={score.id}>
                <td className="px-3 py-2">
                  <Badge type="skill" value={score.category} />
                </td>
                <td className="px-3 py-2">
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold">
                    {score.score}/5
                  </span>
                </td>
                {isAdmin && (
                  <td className="px-3 py-2 text-xs text-slate-600">
                    {score.reviewer_email || 'Unknown reviewer'}
                  </td>
                )}
                <td className="max-w-[280px] px-3 py-2 text-slate-600">
                  {score.note || '-'}
                </td>
              </tr>
            ))}
            {!scores.length && (
              <tr>
                <td
                  className="px-3 py-4 text-sm text-slate-500"
                  colSpan={isAdmin ? 4 : 3}
                >
                  No visible scores yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ScoreForm({ candidate, form, onChange, onSubmit }) {
  const skills = candidate.skills || []

  return (
    <form className="border border-slate-200 p-3" onSubmit={onSubmit}>
      <h3 className="font-semibold">Submit score</h3>
      <select
        className="mt-3 w-full border border-slate-300 px-3 py-2 text-sm"
        value={form.category}
        onChange={(event) => onChange({ ...form, category: event.target.value })}
        required
      >
        <option value="">Select candidate skill</option>
        {skills.map((skill) => (
          <option key={skill} value={skill}>
            {skill}
          </option>
        ))}
      </select>
      <select
        className="mt-3 w-full border border-slate-300 px-3 py-2 text-sm"
        value={form.score}
        onChange={(event) => onChange({ ...form, score: event.target.value })}
      >
        {[1, 2, 3, 4, 5].map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
      <textarea
        className="mt-3 min-h-24 w-full border border-slate-300 px-3 py-2 text-sm"
        placeholder="Optional note"
        value={form.note}
        onChange={(event) => onChange({ ...form, note: event.target.value })}
      />
      <button className="mt-3 w-full bg-slate-950 px-3 py-2 text-sm font-medium text-white">
        Save score
      </button>
    </form>
  )
}

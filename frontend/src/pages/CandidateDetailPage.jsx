import CandidateDetail from '../components/CandidateDetail'

export default function CandidateDetailPage({
  candidate,
  isAdmin,
  loading,
  message,
  streamStatus,
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
  return (
    <section className="min-h-[600px] border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3 text-sm text-slate-600">
        <span>Score stream: {streamStatus}</span>
        <span>{isAdmin ? 'Admin view' : 'Reviewer view'}</span>
      </div>
      <CandidateDetail
        candidate={candidate}
        isAdmin={isAdmin}
        loading={loading}
        message={message}
        summaryLoading={summaryLoading}
        notesDraft={notesDraft}
        scoreForm={scoreForm}
        statusDraft={statusDraft}
        onGenerateSummary={onGenerateSummary}
        onNotesChange={onNotesChange}
        onSaveNotes={onSaveNotes}
        onScoreChange={onScoreChange}
        onSubmitScore={onSubmitScore}
        onBack={onBack}
        onStatusChange={onStatusChange}
        onSaveStatus={onSaveStatus}
      />
    </section>
  )
}

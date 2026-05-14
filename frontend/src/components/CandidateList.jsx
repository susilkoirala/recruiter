import Badge from './Badge'

export default function CandidateList({
  candidates,
  selectedId,
  loading,
  page,
  pageSize,
  onSelect,
  onPageChange,
}) {
  return (
    <section className="border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 p-4">
        <h2 className="text-sm font-semibold">Candidates</h2>
        {loading && <span className="text-xs text-slate-500">Loading</span>}
      </div>
      <div className="hidden grid-cols-[1.2fr_1fr_110px_1.4fr] gap-4 border-b border-slate-200 bg-slate-50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500 md:grid">
        <span>Name</span>
        <span>Role</span>
        <span>Status</span>
        <span>Skills</span>
      </div>
      <div className="divide-y divide-slate-100">
        {candidates.map((candidate) => (
          <button
            key={candidate.id}
            className={`grid w-full gap-2 px-4 py-3 text-left text-sm md:grid-cols-[1.2fr_1fr_110px_1.4fr] ${
              selectedId === candidate.id ? 'bg-teal-50' : 'bg-white'
            }`}
            onClick={() => onSelect(candidate.id)}
          >
            <div>
              <p className="font-medium">{candidate.name}</p>
              <p className="text-xs text-slate-500">{candidate.email}</p>
            </div>
            <div><Badge type="role" value={candidate.role_applied} /></div>
            <div><Badge type="status" value={candidate.status} /></div>
            <div className="flex flex-wrap gap-1">
              {candidate.skills?.slice(0, 4).map((skill) => (
                <Badge key={skill} type="skill" value={skill} />
              ))}
              {candidate.skills?.length > 4 && (
                <span className="text-xs text-slate-500">+{candidate.skills.length - 4}</span>
              )}
            </div>
          </button>
        ))}
        {!candidates.length && (
          <p className="p-4 text-sm text-slate-500">No candidates found.</p>
        )}
      </div>
      <div className="flex items-center justify-between border-t border-slate-200 p-3">
        <button
          className="border border-slate-300 px-3 py-1 text-sm disabled:opacity-40"
          disabled={page === 1}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </button>
        <span className="text-sm text-slate-500">Page {page}</span>
        <button
          className="border border-slate-300 px-3 py-1 text-sm disabled:opacity-40"
          disabled={candidates.length < pageSize}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </button>
      </div>
    </section>
  )
}
